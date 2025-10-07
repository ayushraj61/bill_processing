import os
import re
import json
from datetime import datetime
import pdfplumber
from functools import lru_cache
from sqlalchemy import create_engine, text

# Reuse the same Gemini/Gemma setup approach as BP Oil extractor
_GENAI_AVAILABLE = False

def _load_env_from_file():
    for fname in [".env", "config.env", ".env.local"]:
        path = os.path.join(os.path.dirname(__file__), os.pardir, fname)
        path = os.path.abspath(path)
        try:
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        if "=" in line:
                            k, v = line.split("=", 1)
                            k = k.strip()
                            v = v.strip().strip('"').strip("'")
                            if k and k not in os.environ:
                                os.environ[k] = v
        except Exception:
            continue

try:
    if not os.getenv("GEMINI_API_KEY"):
        _load_env_from_file()
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except:
        pass
    import google.generativeai as genai
    if os.getenv("GEMINI_API_KEY"):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        _GENAI_AVAILABLE = True
except Exception:
    _GENAI_AVAILABLE = False


def _extract_text(pdf_object):
    text = ""
    with pdfplumber.open(pdf_object) as pdf:
        for page in pdf.pages:
            text += (page.extract_text(x_tolerance=2, y_tolerance=2) or "") + "\n"
    return text


def _infer_supplier_from_text(text: str) -> str | None:
    """Best-effort heuristic to find supplier name from top of the bill."""
    if not text:
        return None
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    candidates = []
    blacklist = {"invoice", "tax invoice", "vat invoice", "statement", "page", "summary"}
    for ln in lines[:20]:  # only top of the page
        low = ln.lower()
        if any(b in low for b in blacklist):
            continue
        if re.search(r"[A-Za-z]", ln) and len(ln) >= 3:
            candidates.append(ln)
    prefer = [
        ln for ln in candidates
        if re.search(r"kitchen|restaurant|supermart|ltd|limited|pvt|station|service|services|store|mart|fuel|petrol|garage|company|co\.?", ln, re.I)
    ]
    if prefer:
        return prefer[0]
    return candidates[0] if candidates else None

def _extract_invoice_date_fallback(text: str) -> str | None:
    """Try common date patterns and normalize to YYYY-MM-DD."""
    if not text:
        return None
    m = re.search(r"(20\d{2})[-/.](\d{1,2})[-/.](\d{1,2})", text)
    if m:
        y, mo, d = map(int, m.groups())
        try:
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except Exception:
            pass
    m = re.search(r"(\d{1,2})[/. -](\d{1,2})[/. -](20\d{2})", text)
    if m:
        d, mo, y = map(int, m.groups())
        try:
            return f"{y:04d}-{mo:02d}-{d:02d}"
        except Exception:
            pass
    return None

def _safe_parse_llm_json(resp) -> dict | None:
    raw = None
    try:
        if hasattr(resp, 'text') and resp.text:
            raw = resp.text
    except Exception:
        raw = None
    if not raw:
        return None
    s = raw.strip()
    if s.startswith("```"):
        s = re.sub(r"```(?:json)?", "", s).strip()
    # Handle both single object and array responses
    # First try to find an array
    array_match = re.search(r"\[\s*\{[\s\S]*\}\s*\]", s)
    if array_match:
        try:
            return json.loads(array_match.group(0))
        except Exception:
            pass
    # Then try single object
    m = re.search(r"\{[\s\S]*\}", s)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None

# --- Dept mapping by Post Code (use site_mappings table) ---
DATABASE_URL = "postgresql://postgres:AR%22%28M%28NB%28Qe%5B%22c9J@136.112.86.19:5432/postgres"
_engine = create_engine(DATABASE_URL)

@lru_cache(maxsize=1)
def _load_postcode_to_dept() -> dict:
    try:
        with _engine.begin() as conn:
            rows = conn.execute(text("SELECT post_code, dept FROM site_mappings WHERE post_code IS NOT NULL AND dept IS NOT NULL")).mappings().all()
        mapping = {}
        for r in rows:
            pc = (r["post_code"] or "").upper().replace(" ", "")
            if pc:
                mapping[pc] = str(r["dept"]) if r["dept"] is not None else None
        return mapping
    except Exception:
        return {}

@lru_cache(maxsize=1)
def _load_nominal_codes() -> list:
    """Load all nominal codes from database for AI matching"""
    try:
        with _engine.begin() as conn:
            rows = conn.execute(text("SELECT code, object_name FROM nominal_code ORDER BY code")).mappings().all()
        codes = []
        for r in rows:
            codes.append({
                'code': r["code"],
                'object_name': r["object_name"]
            })
        return codes
    except Exception as e:
        print(f"Error loading nominal codes: {e}")
        return []

def _match_description_to_nc_with_ai(description: str) -> str | None:
    """Use AI to match item description with nominal code object names"""
    if not _GENAI_AVAILABLE or not description:
        return None
    
    try:
        nominal_codes = _load_nominal_codes()
        if not nominal_codes:
            return None
        
        # Create a mapping string for the AI
        codes_str = "\n".join([f"{nc['code']}: {nc['object_name']}" for nc in nominal_codes])
        
        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""You are an accounting code matcher.

Given this item description: "{description}"

Match it to the MOST APPROPRIATE nominal code from this list:

{codes_str}

RULES:
- Return ONLY the 4-digit code (e.g., "7550")
- If NO good match exists, return "null"
- Match by context and meaning, not exact words
- Examples:
  * "SIM card fee" → "7550" (Telephone and Fax)
  * "Card processing hardware" → "7905" (Card Processing Hardware)
  * "Grocery items" → "5000" (Materials Purchased)
  * "Restaurant bill" → "5000" (Materials Purchased)
  * "Office supplies" → "7902" (Stationery)

Return ONLY the code or "null", nothing else."""

        resp = model.generate_content([prompt])
        result = resp.text.strip().replace('"', '').replace("'", "")
        
        if result.lower() == 'null' or not result.isdigit():
            return None
        
        return result
        
    except Exception as e:
        print(f"AI N/C matching error: {e}")
        return None

def _extract_postcode_uk(text: str) -> str | None:
    if not text:
        return None
    # UK postcode pattern (simple form) - matches HP6 6FA, WD3 4ER, etc.
    m = re.search(r"\b[A-Z]{1,2}\d[\dA-Z]?\s?\d[A-Z]{2}\b", text, re.I)
    if m:
        postcode = m.group(0).upper()
        print(f"[DEBUG] Extracted postcode: {postcode}")
        return postcode
    return None

# ---------- Amount helpers (Subtotal / VAT / Total) ----------
def _amount_from_match_group(g: str) -> float | None:
    try:
        s = re.sub(r"[^0-9.]+", "", g)
        if not s:
            return None
        # collapse multiple dots
        if s.count('.') > 1:
            parts = s.split('.')
            s = ''.join(parts[:-1]) + '.' + parts[-1]
        return float(s)
    except Exception:
        return None

def _find_first_amount(text: str, label_regexes: list[str]) -> float | None:
    for pat in label_regexes:
        m = re.search(pat, text, re.I)
        if m:
            for grp in m.groups()[::-1]:  # prefer last group
                if grp is None:
                    continue
                amt = _amount_from_match_group(grp)
                if amt is not None:
                    return amt
    return None

def _find_subtotal_amount(text: str) -> float | None:
    patterns = [
        r"\bsub\s*total\b[^\n]*?([0-9,.]+)\b",
        r"\bsub\s*tot\b[^\n]*?([0-9,.]+)\b",
        r"\bsubtotal\b[^\n]*?([0-9,.]+)\b",
        r"\bamount\s*before\s*tax\b[^\n]*?([0-9,.]+)\b",
        r"\bnet\s*amount\b[^\n]*?([0-9,.]+)\b",
    ]
    return _find_first_amount(text, patterns)

def _find_vat_amount(text: str) -> float | None:
    # Prefer a single VAT/Tax total line
    patterns_total = [
        r"\b(total\s*gst|gst\s*total|vat\s*total|total\s*tax)\b[^\n]*?([0-9,.]+)\b",
    ]
    vat = _find_first_amount(text, patterns_total)
    if vat is not None:
        return vat
    # Else sum components (CGST/SGST/UTGST/IGST)
    comp_labels = ["cgst", "sgst", "utgst", "igst", "vat"]
    total = 0.0
    found = False
    for lab in comp_labels:
        for m in re.finditer(rf"\b{lab}\b[^\n]*?([0-9,.]+)\b", text, re.I):
            amt = _amount_from_match_group(m.group(1))
            if amt is not None:
                total += amt
                found = True
    return total if found else None

def _find_grand_total(text: str) -> float | None:
    patterns = [
        r"\bgrand\s*total\b[^\n]*?([0-9,.]+)\b",
        r"\btotal\b[^\n]*?([0-9,.]+)\b",
        r"\bamount\s*payable\b[^\n]*?([0-9,.]+)\b",
        r"\bamount\s*received\b[^\n]*?([0-9,.]+)\b",
    ]
    return _find_first_amount(text, patterns)

def process_bill_objectified(pdf_object, filename, upload_date):
    """Extract individual line items from the bill for Objectify mode."""
    if hasattr(pdf_object, "seek"):
        pdf_object.seek(0)
    text = _extract_text(pdf_object)
    
    
    supplier = "Other"
    invoice_date_iso = None
    gross_amount = "0.00"
    line_items = []
    
    # Extract invoice reference from filename or text
    # All variations stored as 'bill_reference_number' in database
    invoice_reference = None
    try:
        # Try to extract from filename first
        ref_match = re.search(r"(\d{4,})", filename or "")
        if ref_match:
            invoice_reference = ref_match.group(1)
        else:
            # Try to extract from text using comprehensive search patterns
            # Supports numbers with hyphens, slashes, spaces (e.g., 413108010-001755)
            ref_patterns = [
                # Invoice variations (with separators)
                r"invoice\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"invoice\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"invoice\s*number\s*:?\s*([\d\-\/\s]+)",
                r"inv\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"inv\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"inv\s*:?\s*([\d\-\/\s]+)",
                # Bill variations (with separators)
                r"bill\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*number\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*ref\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*reference\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*dt\s*:?\s*[\d\/\-\s]+\s+vou\s*\.?\s*:?\s*([\d\-\/\s]+)",  # "Bill Dt : 12/08/2025 Vou.:5019010-0133"
                # Reference variations (with separators)
                r"ref\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"ref\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"reference\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"reference\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"reference\s*number\s*:?\s*([\d\-\/\s]+)",
                # Document variations (with separators)
                r"doc\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"doc\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"document\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"document\s*number\s*:?\s*([\d\-\/\s]+)",
                # Receipt variations (with separators)
                r"receipt\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"receipt\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"receipt\s*number\s*:?\s*([\d\-\/\s]+)",
                # Order variations (with separators)
                r"order\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"order\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"order\s*number\s*:?\s*([\d\-\/\s]+)",
                # Transaction variations (with separators)
                r"transaction\s*id\s*:?\s*([\d\-\/\s]+)",
                r"transaction\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"trans\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"trans\s*#?\s*:?\s*([\d\-\/\s]+)",
                # Voucher variations (with separators)
                r"voucher\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"voucher\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"voucher\s*number\s*:?\s*([\d\-\/\s]+)",
            ]
            for pattern in ref_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    # Clean up the captured reference (remove extra spaces, keep hyphens/slashes)
                    invoice_reference = re.sub(r'\s+', '', match.group(1).strip())
                    break
    except Exception:
        invoice_reference = None
    
    if _GENAI_AVAILABLE:
        try:
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            model = genai.GenerativeModel(model_name)
            
            # Enhanced prompt for extracting individual items
            prompt = (
                "Read this PDF invoice and extract ALL individual line items/products.\n\n"
                "Return a JSON ARRAY where each object represents ONE line item with keys:\n"
                "['Type','A/C','Date','Ref','Ex.Ref','N/C','Dept','Details','Net','T/C','VAT','Supplier','PostCode'].\n\n"
                "CRITICAL RULES:\n"
                "- Create one object for EACH product/service line in the invoice (per-item), not the overall totals.\n"
                "- DO NOT include 'Total', 'Sub Total', 'Grand Total', or summary rows as items.\n"
                "- Details: the exact description for that line; keep concise.\n"
                "- Net: net amount for that specific item only.\n"
                "- VAT: VAT amount for that specific item only. If only a single VAT total is shown, compute a UNIFORM VAT RATE = (overall VAT total / overall Net total) and set per-item VAT = item Net * uniform rate. Round to 2 decimals and reconcile any rounding difference by adjusting the last item's VAT so that sum(item VAT) exactly matches the document VAT total. If both a VAT total and item gross are present, prefer using the uniform rate from totals. Otherwise, proportionally distribute by net.\n"
                "- If only a gross per-item is available, infer per-item VAT by the tax rate applied on that item and derive per-item net accordingly.\n\n"
                "For each item:\n"
                "- Type='PI'; 'A/C'=null; 'N/C'=null; 'Dept'=null\n"
                "- Date=invoice date in YYYY-MM-DD\n"
                "- Ref=ONLY numeric part from filename (NOT invoice number from text). If filename has no numbers, Ref should be empty or null\n"
                "- Ex.Ref=<Month'YY>/<last-3 of Ref>\n"
                "- Compute T/C based on VAT rate: T1≈20%, T5≈5%, T0≈0% (else T2; T9 if unknown)\n"
                "- Extract UK PostCode if present\n\n"
                "Return ONLY the JSON array (no markdown, no explanation). Ensure sum(Net) and sum(VAT) over items match the invoice totals (after rounding reconciliation)."
            )
            
            # Upload file to Gemini
            if hasattr(pdf_object, "seek"):
                pdf_object.seek(0)
            tmp_path = "/tmp/_upload_invoice_obj.pdf"
            with open(tmp_path, "wb") as tmpf:
                tmpf.write(pdf_object.read())
            uploaded = genai.upload_file(tmp_path)
            resp = model.generate_content([prompt, uploaded])
            data = _safe_parse_llm_json(resp)
            
            if data:
                # Handle both single object and array responses
                if isinstance(data, dict):
                    data = [data]  # Convert to array
                
                # Process each line item
                for item in data:
                    if not isinstance(item, dict):
                        continue
                    item.setdefault('Type', 'PI')
                    item.setdefault('A/C', None)
                    item.setdefault('N/C', None)
                    item.setdefault('Dept', None)
                    
                    # Extract supplier from first item
                    if not supplier or supplier == "Other":
                        supplier = item.get('Supplier', supplier)
                    
                    # Set Ref to show where file will go after approval
                    # Format: Approved/CompanyName/YYYY-MM/Filename
                    try:
                        # Get current date for month folder
                        from datetime import datetime
                        current_month = datetime.now().strftime('%Y-%m')
                        
                        # For now, assume PRL (will be dynamic when multiple companies)
                        company_name = "PRL"  # This will be determined from file location in future
                        
                        # Generate drive address showing where file will go
                        drive_address = f"Approved/{company_name}/{current_month}/{filename}"
                        item['Ref'] = drive_address
                        
                    except Exception as e:
                        # Fallback to filename if drive address generation fails
                        item['Ref'] = filename or "Unknown"
                    
                    
                    # Generate Ex.Ref if missing
                    if not item.get('Ex.Ref'):
                        try:
                            d = item.get('Date')
                            dt = datetime.strptime(d, '%Y-%m-%d') if d else None
                            ref = str(item.get('Ref') or '')
                            last3 = ref[-3:] if len(ref) >= 3 else ref
                            if dt:
                                item['Ex.Ref'] = f"{dt.strftime('%B')[:3]}'{dt.strftime('%y')}/{last3}"
                        except Exception:
                            pass
                    
                    # Map Dept via PostCode
                    postcode = item.get('PostCode') or _extract_postcode_uk(text)
                    if (not item.get('Dept')) and postcode:
                        pc_norm = postcode.upper().replace(' ', '')
                        dept_map = _load_postcode_to_dept()
                        if pc_norm in dept_map and dept_map[pc_norm]:
                            item['Dept'] = dept_map[pc_norm]
                    
                    # Map N/C using AI matching with description (Itemize mode - per item)
                    if not item.get('N/C'):
                        details = item.get('Details', '')
                        if details:
                            matched_nc = _match_description_to_nc_with_ai(details)
                            if matched_nc:
                                item['N/C'] = matched_nc
                                print(f"[AI N/C Match] '{details}' → {matched_nc}")
                    
                    # Calculate T/C if missing
                    if not item.get('T/C'):
                        try:
                            n = float(str(item.get('Net') or 0))
                            v = float(str(item.get('VAT') or 0))
                            rate = (v / n) * 100 if n else None
                            if rate is not None:
                                if 19.0 <= rate <= 21.0:
                                    item['T/C'] = 'T1'
                                elif 4.0 <= rate <= 6.0:
                                    item['T/C'] = 'T5'
                                elif 0.0 <= rate <= 0.3:
                                    item['T/C'] = 'T0'
                                else:
                                    item['T/C'] = 'T2'
                            else:
                                item['T/C'] = 'T9'
                        except Exception:
                            item['T/C'] = 'T9'
                    
                    # Create clean line item (remove Supplier/PostCode)
                    cols = ['Type','A/C','Date','Ref','Ex.Ref','N/C','Dept','Details','Net','T/C','VAT']
                    line = {k: item.get(k) for k in cols}
                    line_items.append(line)
                
                # Extract invoice date from first item
                if line_items:
                    invoice_date_iso = line_items[0].get('Date')
                
                # Calculate total gross amount
                try:
                    total_net = sum(float(str(item.get('Net', 0))) for item in line_items)
                    total_vat = sum(float(str(item.get('VAT', 0))) for item in line_items)
                    gross_amount = f"{(total_net + total_vat):.2f}"
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"Objectify extraction error: {e}")
            # Fall back to single line item
            line_items = [{"error": f"Objectify extraction failed: {e}"}]
    
    # If no items extracted, return single total item
    if not line_items:
        # Fall back to total mode extraction
        result = process_bill(pdf_object, filename, upload_date)
        return result
    
    return {
        'dashboard_data': {
            'supplier_name': supplier,
            'invoice_date': invoice_date_iso,
            'gross_amount': gross_amount,
            'dynamic_filename': None,
            'invoice_reference': invoice_reference,
        },
        'line_items': line_items,
    }

def process_bill(pdf_object, filename, upload_date):
    """Generic extractor for non-standard suppliers using Gemini - Total mode."""
    if hasattr(pdf_object, "seek"):
        pdf_object.seek(0)
    text = _extract_text(pdf_object)

    supplier = "Other"
    invoice_date_iso = None
    gross_amount = "0.00"
    line: dict = {}

    if _GENAI_AVAILABLE:
        try:
            model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
            model = genai.GenerativeModel(model_name)
            # Ask LLM to read the PDF file directly (no pdfplumber text); include PostCode for mapping
            prompt = (
                "Read this PDF and return ONE JSON object with keys "
                "['Type','A/C','Date','Ref','Ex.Ref','N/C','Dept','Details','Net','T/C','VAT','Supplier','PostCode'].\n\n"
                "Supplier: printed business title/company in header. Do not infer from filename.\n"
                "Type='PI'; 'A/C'=null; 'N/C'=null; 'Dept'=null (ALWAYS null - will be mapped from PostCode);\n"
                "Date=YYYY-MM-DD; Ref=ONLY numeric part from filename (NOT invoice number from text). If filename has no numbers, Ref should be empty or null; Ex.Ref=<Month'YY>/<last-3 of Ref>;\n"
                "Details=a short human summary;\n"
                "Amounts: Sub Total/Net before tax → Net; VAT/Tax total → VAT; Total/Grand Total → Gross (but still output Net & VAT).\n"
                "Compute VAT% = VAT/Net and set T/C: T1≈20%, T5≈5%, T0≈0%, else T2, T9 if unknown.\n"
                "IMPORTANT: Extract UK PostCode (like WD3 4ER) if present as 'PostCode' - this will be used to map Dept number.\n"
                "Return ONLY valid JSON (no markdown)."
            )

            # Upload file to Gemini and request parsing
            if hasattr(pdf_object, "seek"):
                pdf_object.seek(0)
            tmp_path = "/tmp/_upload_invoice.pdf"
            with open(tmp_path, "wb") as tmpf:
                tmpf.write(pdf_object.read())
            uploaded = genai.upload_file(tmp_path)
            resp = model.generate_content([prompt, uploaded])
            data = _safe_parse_llm_json(resp)
            if data:
                # Handle array response (take first item)
                if isinstance(data, list):
                    data = data[0] if data else {}
                    
                data.setdefault('Type', 'PI')
                data.setdefault('A/C', None)
                data.setdefault('N/C', None)
                data.setdefault('Dept', None)
                supplier = data.get('Supplier') or supplier
                if not data.get('Ref'):
                    m = re.search(r"(\d{6,})", filename)
                    if m:
                        data['Ref'] = m.group(1)
                if not data.get('Ex.Ref'):
                    try:
                        d = data.get('Date')
                        dt = datetime.strptime(d, '%Y-%m-%d') if d else None
                        ref = str(data.get('Ref') or '')
                        last3 = ref[-3:] if len(ref) >= 3 else ref
                        if dt:
                            data['Ex.Ref'] = f"{dt.strftime('%B')[:3]}'{dt.strftime('%y')}/{last3}"
                    except Exception:
                        pass
                # Map Dept via PostCode if Dept absent
                postcode = data.get('PostCode') or _extract_postcode_uk(text)
                print(f"[DEBUG] PostCode from LLM: {data.get('PostCode')}, from text extraction: {_extract_postcode_uk(text) if not data.get('PostCode') else 'N/A'}")
                if (not data.get('Dept')) and postcode:
                    pc_norm = postcode.upper().replace(' ', '')
                    print(f"[DEBUG] Normalized postcode: {pc_norm}")
                    dept_map = _load_postcode_to_dept()
                    print(f"[DEBUG] Available postcodes in DB: {list(dept_map.keys())}")
                    if pc_norm in dept_map and dept_map[pc_norm]:
                        data['Dept'] = dept_map[pc_norm]
                        print(f"[DEBUG] Mapped Dept: {data['Dept']}")
                    else:
                        print(f"[DEBUG] No mapping found for postcode: {pc_norm}")
                
                # Map N/C using AI matching with description (Consolidate mode - single item)
                if not data.get('N/C'):
                    details = data.get('Details', '')
                    if details:
                        matched_nc = _match_description_to_nc_with_ai(details)
                        if matched_nc:
                            data['N/C'] = matched_nc
                            print(f"[AI N/C Match] '{details}' → {matched_nc}")
                
                # FORCE Ref to be from filename only (override LLM completely)
                m = re.search(r"(\d{6,})", filename)
                if m:
                    data['Ref'] = m.group(1)
                else:
                    data['Ref'] = None  # No numeric part in filename
                
                # Normalize output columns to match BP Oil preview (drop Supplier/PostCode)
                cols = ['Type','A/C','Date','Ref','Ex.Ref','N/C','Dept','Details','Net','T/C','VAT']
                line = {k: data.get(k) for k in cols}
                base_fn = os.path.splitext(os.path.basename(filename))[0].lower().replace('_',' ').strip()
                if (not supplier or supplier.strip().lower() == "other"):
                    fallback = _infer_supplier_from_text(text)
                    if fallback:
                        supplier = fallback
                if base_fn.startswith("whatsapp image"):
                    fb = _infer_supplier_from_text(text)
                    if fb:
                        supplier = fb
                invoice_date_iso = data.get('Date') or _extract_invoice_date_fallback(text)
                if not data.get('Details'):
                    details = None
                    if re.search(r"restaurant|kitchen|cafe|cash/bill|gst", text, re.I):
                        details = "Restaurant invoice"
                    data['Details'] = details or (supplier if supplier and isinstance(supplier, str) else "Invoice")
                # Ensure Net, VAT, Gross using fallback scan of bill text
                try:
                    net_val = data.get('Net')
                    vat_val = data.get('VAT')
                    if net_val in (None, "", 0):
                        st = _find_subtotal_amount(text)
                        if st is not None:
                            data['Net'] = st
                            net_val = st
                    if vat_val in (None, "", 0):
                        vt = _find_vat_amount(text)
                        if vt is not None:
                            data['VAT'] = vt
                            vat_val = vt
                    # Gross = Net + VAT
                    n = float(str(net_val or 0))
                    v = float(str(vat_val or 0))
                    gross_amount = f"{(n+v):.2f}"
                except Exception:
                    pass
                if not data.get('T/C'):
                    try:
                        n = float(str(data.get('Net') or 0))
                        v = float(str(data.get('VAT') or 0))
                        rate = (v / n) * 100 if n else None
                        if rate is not None:
                            if 19.0 <= rate <= 21.0:
                                data['T/C'] = 'T1'
                            elif 4.0 <= rate <= 6.0:
                                data['T/C'] = 'T5'
                            elif 0.0 <= rate <= 0.3:
                                data['T/C'] = 'T0'
                            else:
                                data['T/C'] = 'T2'
                        else:
                            data['T/C'] = 'T9'
                    except Exception:
                        data['T/C'] = data.get('T/C') or 'T9'
                        
                # Update line dict with processed data
                line = {k: data.get(k) for k in ['Type','A/C','Date','Ref','Ex.Ref','N/C','Dept','Details','Net','T/C','VAT']}
                
        except Exception as e:
            # LLM service temporarily unavailable, using fallback extraction
            if "503" in str(e) or "Service Unavailable" in str(e):
                print(f"LLM service temporarily unavailable, using fallback extraction")
            else:
                print(f"LLM extraction failed: {e}")
            line = {"error": f"LLM extraction failed: {e}"}

    if not line:
        ref = None
        m = re.search(r"(\d{6,})", filename)
        if m:
            ref = m.group(1)
        date_fb = _extract_invoice_date_fallback(text)
        ex_ref = None
        try:
            if date_fb and ref:
                dt = datetime.strptime(date_fb, '%Y-%m-%d')
                ex_ref = f"{dt.strftime('%B')[:3]}'{dt.strftime('%y')}/{ref[-3:]}"
        except Exception:
            ex_ref = None
        supplier_fb = _infer_supplier_from_text(text) or supplier
        # Set Ref to show where file will go after approval
        if not ref:
            try:
                from datetime import datetime
                current_month = datetime.now().strftime('%Y-%m')
                company_name = "PRL"  # Will be dynamic when multiple companies
                ref = f"Approved/{company_name}/{current_month}/{filename}"
            except Exception:
                ref = filename or "Unknown"
        
        line = {
            'Type': 'PI', 'A/C': None, 'Date': date_fb, 'Ref': ref, 'Ex.Ref': ex_ref,
            'N/C': None, 'Dept': None, 'Details': supplier_fb, 'Net': None, 'T/C': None, 'VAT': None,
        }
        supplier = supplier_fb
        invoice_date_iso = date_fb
        
        # Calculate gross amount from Net + VAT for fallback
        try:
            net_val = _find_subtotal_amount(text)
            vat_val = _find_vat_amount(text)
            if net_val is not None and vat_val is not None:
                gross_amount = f"{(net_val + vat_val):.2f}"
        except Exception:
            pass

    # Extract invoice reference from filename or text
    # All variations stored as 'bill_reference_number' in database
    invoice_reference = None
    try:
        # Try to extract from filename first
        ref_match = re.search(r"(\d{4,})", filename or "")
        if ref_match:
            invoice_reference = ref_match.group(1)
        else:
            # Try to extract from text using comprehensive search patterns
            # Supports numbers with hyphens, slashes, spaces (e.g., 413108010-001755)
            ref_patterns = [
                # Invoice variations (with separators)
                r"invoice\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"invoice\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"invoice\s*number\s*:?\s*([\d\-\/\s]+)",
                r"inv\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"inv\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"inv\s*:?\s*([\d\-\/\s]+)",
                # Bill variations (with separators)
                r"bill\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*number\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*ref\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*reference\s*:?\s*([\d\-\/\s]+)",
                r"bill\s*dt\s*:?\s*[\d\/\-\s]+\s+vou\s*\.?\s*:?\s*([\d\-\/\s]+)",  # "Bill Dt : 12/08/2025 Vou.:5019010-0133"
                # Reference variations (with separators)
                r"ref\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"ref\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"reference\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"reference\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"reference\s*number\s*:?\s*([\d\-\/\s]+)",
                # Document variations (with separators)
                r"doc\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"doc\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"document\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"document\s*number\s*:?\s*([\d\-\/\s]+)",
                # Receipt variations (with separators)
                r"receipt\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"receipt\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"receipt\s*number\s*:?\s*([\d\-\/\s]+)",
                # Order variations (with separators)
                r"order\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"order\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"order\s*number\s*:?\s*([\d\-\/\s]+)",
                # Transaction variations (with separators)
                r"transaction\s*id\s*:?\s*([\d\-\/\s]+)",
                r"transaction\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"trans\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"trans\s*#?\s*:?\s*([\d\-\/\s]+)",
                # Voucher variations (with separators)
                r"voucher\s*no\s*\.?\s*:?\s*([\d\-\/\s]+)",
                r"voucher\s*#?\s*:?\s*([\d\-\/\s]+)",
                r"voucher\s*number\s*:?\s*([\d\-\/\s]+)",
            ]
            for pattern in ref_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    # Clean up the captured reference (remove extra spaces, keep hyphens/slashes)
                    invoice_reference = re.sub(r'\s+', '', match.group(1).strip())
                    break
    except Exception:
        invoice_reference = None

    return {
        'dashboard_data': {
            'supplier_name': supplier,
            'invoice_date': invoice_date_iso,
            'gross_amount': gross_amount,
            'dynamic_filename': None,
            'invoice_reference': invoice_reference,
        },
        'line_items': [line],
    }

# Note: The advanced process_bill_objectified is defined above (around line ~219)