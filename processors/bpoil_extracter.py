import re
import os
import json
from datetime import datetime
import pdfplumber
from functools import lru_cache
from sqlalchemy import create_engine, text

# --- Gemini/Gemma Configuration ---
_GENAI_AVAILABLE = False

# --- Database config for site mappings (kept local to extractor) ---
DATABASE_URL = "postgresql://bill_user:ayush23854@localhost/bill_processor_db"
_engine = create_engine(DATABASE_URL, pool_pre_ping=True)

def _load_env_from_file():
    """Load KEY=VALUE pairs from .env file"""
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
        print("Gemini/Gemma API configured successfully")
except Exception as e:
    print(f"Gemini/Gemma not available: {e}")
    _GENAI_AVAILABLE = False

@lru_cache(maxsize=1)
def load_site_mappings():
    """Load site mappings from the database once and cache in-memory.
    Returns two dicts: site_to_dept, site_to_short.
    """
    try:
        with _engine.begin() as conn:
            rows = conn.execute(
                text("SELECT site_name, dept, short_code FROM site_mappings")
            ).mappings().all()
        site_to_dept = {}
        site_to_short = {}
        for r in rows:
            name = r["site_name"]
            if name:
                if r["dept"] is not None:
                    site_to_dept[name] = str(r["dept"])
                if r["short_code"]:
                    site_to_short[name] = r["short_code"]
        return site_to_dept, site_to_short
    except Exception as e:
        print(f"[BP OIL] Failed to load site mappings from DB: {e}")
        return {}, {}

def _resolve_site_fields(site_name_from_invoice: str):
    """Fuzzy resolve a site to its dept and short code from DB."""
    from fuzzywuzzy import process as fz_process
    site_to_dept, site_to_short = load_site_mappings()
    catalog = list(site_to_dept.keys() | site_to_short.keys())
    if not catalog:
        return None, None, None  # resolved_name, dept, short
    try:
        best, score = fz_process.extractOne(site_name_from_invoice, catalog)
    except Exception:
        best, score = (site_name_from_invoice, 0)
    resolved = best if score and score >= 80 else site_name_from_invoice
    dept = site_to_dept.get(resolved)
    short = site_to_short.get(resolved)
    return resolved, dept, short

def _extract_text(pdf_object):
    """Extract text from PDF using pdfplumber"""
    text = ""
    with pdfplumber.open(pdf_object) as pdf:
        for page in pdf.pages:
            text += (page.extract_text(x_tolerance=2, y_tolerance=2) or "") + "\n"
    return text

def _extract_with_gemini(text, filename):
    """Extract all data using Gemini/Gemma API"""
    if not _GENAI_AVAILABLE:
        return None
    
    try:
        # Pull latest mappings from DB for the LLM prompt
        site_to_dept, site_to_short = load_site_mappings()
        dept_json = json.dumps(site_to_dept, indent=2, ensure_ascii=False)
        short_json = json.dumps(site_to_short, indent=2, ensure_ascii=False)

        model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Extract reference number from filename or text using multiple patterns
        file_num = None
        
        # Try filename first
        mref = re.search(r"(\d{6,})", filename)
        if mref:
            file_num = mref.group(1)
        else:
            # Try to extract from text using multiple search terms
            ref_patterns = [
                r"invoice\s*#?\s*:?\s*(\d{4,})",
                r"invoice\s*no\s*:?\s*(\d{4,})",
                r"invoice\s*number\s*:?\s*(\d{4,})",
                r"ref\s*#?\s*:?\s*(\d{4,})",
                r"reference\s*#?\s*:?\s*(\d{4,})",
                r"reference\s*number\s*:?\s*(\d{4,})",
                r"bill\s*#?\s*:?\s*(\d{4,})",
                r"bill\s*number\s*:?\s*(\d{4,})",
            ]
            for pattern in ref_patterns:
                match = re.search(pattern, text, re.I)
                if match:
                    file_num = match.group(1)
                    break
        
        # Create comprehensive prompt with all mappings
        prompt = f"""You are an expert invoice parser for BP Oil UK Limited invoices. 
Extract a single JSON object with these EXACT keys:
['Type','A/C','Date','Ref','Ex.Ref','N/C','Dept','Details','Net','T/C','VAT']

USE THESE EXACT MAPPINGS:

SITE TO DEPARTMENT MAPPING:
{dept_json}

EXTRACTION RULES:
1. Type: Always 'PI'
 2. A/C: Prefer DB short_code (below). Build A/C as UPPER(short_code)+'BPOIL'. If short_code not found, use first 3 letters of the resolved site name + 'BPOIL'.
    SITE TO SHORT CODE MAPPING:
{short_json}
3. Date: Invoice Date in ISO format YYYY-MM-DD
4. Ref: Use the numeric part from filename: {file_num or 'unknown'}
5. Ex.Ref: Format as <Month'YY>/SI/BP/Sim/<last-3-digits-of-Ref>
   Example: August'25/SI/BP/Sim/503
6. N/C: 
   - '7550' if description contains 'sim' or 'SIM'
   - '7905' if description contains 'card process'
 7. Dept: Find the site name, then use SITE_TO_DEPT mapping above
 8. Details: Prefer DB short_code (3–5 letters) for the site if available; else first 3 letters of site. Format as '<short>-<Description> <Period-dates>'
   Example: 'Can-Card Process h.ware 02.07.2025-01.08.2025'
9. Net: The 'Value Ex. VAT (GBP)' amount from FIRST data row (NOT the Total row)
10. VAT: The 'Tax Amount (GBP)' from FIRST data row (NOT the Total row)
11. T/C: Tax code based on VAT rate:
    - 'T1' for 20% VAT
    - 'T5' for 5% VAT
    - 'T0' for 0% VAT
    - 'T2' for other rates
    - 'T9' if unknown

IMPORTANT: 
- Extract from the FIRST DATA ROW in the table, not the Total row
- All monetary values as strings with 2 decimals (e.g., '162.50')
- Site names might be written as "PLATINUM CANKLOW SERVICE STATION" - match to "Canklow Service Station"
- Return ONLY valid JSON object, no markdown, no explanation"""

        inputs = f"INVOICE TEXT:\n{text}"
        
        model = genai.GenerativeModel(model_name)
        resp = model.generate_content([prompt, inputs])
        
        if resp and resp.text:
            # Clean response text
            json_text = resp.text.strip()
            # Remove markdown if present
            if json_text.startswith("```"):
                json_text = re.sub(r"```(?:json)?", "", json_text).strip()
            
            parsed = json.loads(json_text)
            
            if isinstance(parsed, dict):
                # Ensure all required keys exist
                required_keys = ['Type','A/C','Date','Ref','Ex.Ref','N/C','Dept','Details','Net','T/C','VAT']
                for key in required_keys:
                    if key not in parsed:
                        parsed[key] = None
                
                print("Successfully extracted data using Gemini/Gemma")
                return parsed
            
    except Exception as e:
        print(f"Gemini extraction error: {e}")
    
    return None

def process_bill(pdf_object, filename, upload_date):
    """Main processing function using Gemini"""
    try:
        # Extract text from PDF
        if hasattr(pdf_object, "seek"):
            pdf_object.seek(0)
        text = _extract_text(pdf_object)
    except Exception as e:
        return {
            "dashboard_data": {
                "supplier_name": "BP Oil",
                "invoice_date": None,
                "gross_amount": "0.00",
                "dynamic_filename": None
            },
            "line_items": [{"error": f"Could not read PDF: {e}"}]
        }

    # Extract with Gemini
    extracted_data = _extract_with_gemini(text, filename)
    
    if not extracted_data:
        # If Gemini fails, return error
        return {
            'dashboard_data': {
                'supplier_name': 'BP Oil',
                'invoice_date': None,
                'gross_amount': '0.00',
                'dynamic_filename': None,
            },
            'line_items': [{"error": "Gemini extraction failed. Please check API configuration."}],
        }
    
    # Calculate dashboard gross amount
    dashboard_gross = "0.00"
    try:
        net_val = float(str(extracted_data.get('Net', 0)))
        vat_val = float(str(extracted_data.get('VAT', 0)))
        dashboard_gross = f"{(net_val + vat_val):.2f}"
    except:
        dashboard_gross = "0.00"

    # Extract invoice reference from filename
    file_num = None
    mref = re.search(r"(\d{6,})", filename)
    if mref:
        file_num = mref.group(1)
    else:
        # Try to extract from text using multiple search terms
        ref_patterns = [
            r"invoice\s*#?\s*:?\s*(\d{4,})",
            r"invoice\s*no\s*:?\s*(\d{4,})",
            r"invoice\s*number\s*:?\s*(\d{4,})",
            r"ref\s*#?\s*:?\s*(\d{4,})",
            r"reference\s*#?\s*:?\s*(\d{4,})",
            r"reference\s*number\s*:?\s*(\d{4,})",
            r"bill\s*#?\s*:?\s*(\d{4,})",
            r"bill\s*number\s*:?\s*(\d{4,})",
        ]
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.I)
            if match:
                file_num = match.group(1)
                break

    # Generate dynamic filename if needed
    dynamic_filename = None
    try:
        date_str = extracted_data.get('Date', '')
        if date_str:
            # Extract site prefix from Details or A/C
            site_prefix = ""
            if extracted_data.get('Details'):
                site_prefix = extracted_data['Details'].split('-')[0]
            elif extracted_data.get('A/C'):
                site_prefix = extracted_data['A/C'][:3]
            
            # Format: DDMMYYYY_SiteCode_BPOil.pdf
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            dynamic_filename = f"{date_obj.strftime('%d%m%Y')}_{site_prefix}_BPOil.pdf"
    except:
        dynamic_filename = None

    return {
        'dashboard_data': {
            'supplier_name': 'BP Oil',
            'invoice_date': extracted_data.get('Date'),
            'gross_amount': dashboard_gross,
            'dynamic_filename': dynamic_filename,
            'invoice_reference': file_num,
        },
        'line_items': [extracted_data],
    }
