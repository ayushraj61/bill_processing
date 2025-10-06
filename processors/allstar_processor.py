import pdfplumber
import re
import io
from fuzzywuzzy import fuzz, process
from datetime import datetime

# --- MAPPINGS AND CONSTANTS ---
GARAGE_NUMBER_TO_INTERMEDIATE_NAME = {
    "09970184": "Manor", "09971533": "Salterton", "09970124": "Hen & Chicken",
    "09970182": "Luton", "09970823": "Delph", "09970824": "Saxon",
    "09971258": "Gemini", "09971301": "Swan", "09971349": "Filleybrook",
    "09971352": "Vale", "09971302": "Kensington", "09971300": "Country oak",
    "09971433": "King of Segdgley", "09971425": "Gnosall", "09971426": "Ministerly",
    "09971466": "canklow", "09971520": "Yeovil", "18009083": "Jubits",
    "18009849": "Worsley", "09971521": "White Rose", "09971527": "Storrington",
    "18009852": "park View", "18009851": "Lowerlane", "09971534": "Elstow-Jbros",
    "18009853": "Portland", "1332796": "Yeovil"
}
STANDARD_FINAL_NAMES = [
    "Manor Service Station", "Hen & Chicken Service Station", "Salterton Service Station", "Luton Road Connect", 
    "Delph Service Station", "Saxon Service Station", "Jubits Lane", "Worsley Brow", "GEMINI SERVICE STATION", 
    "Parkview", "Filleybrook", "Swan", "Portland", "Lower Lane", "Kensington", "County Oak", "Kings of Sedgley", 
    "Gnosall", "Minsterley", "Yeovil", "Canklow", "Stanton", "White Rose", "Storrington", "Elstow-Jbros"
]

# --- HELPER FUNCTIONS ---
def _preprocess_name_for_matching(name):
    name = name.lower()
    name = re.sub(r'^(bp|val|valero|greenergy)[\s-]*', '', name)
    name = re.sub(r'\b(service station|garage|connect|road|lane|moor)\b', '', name)
    name = re.sub(r'[^\w\s&]', '', name)
    return re.sub(r'\s+|-', '', name)

PROCESSED_FINAL_NAMES = {_preprocess_name_for_matching(name): name for name in STANDARD_FINAL_NAMES}

def _find_best_standard_name(name_to_match):
    if not name_to_match: return "Unknown (Number not in mapping)"
    processed_name = _preprocess_name_for_matching(name_to_match)
    best_match = process.extractOne(processed_name, PROCESSED_FINAL_NAMES.keys(), scorer=fuzz.token_set_ratio)
    return PROCESSED_FINAL_NAMES[best_match[0]] if best_match and best_match[1] > 80 else name_to_match

def _extract_text(pdf_object):
    txt = ""
    with pdfplumber.open(pdf_object) as pdf:
        for p in pdf.pages:
            txt += (p.extract_text(x_tolerance=2, y_tolerance=2) or "") + "\n"
    return txt

def _extract_batch_data(text):
    pattern = r'(\d{2}\.\d{2}\.\d{4})\s+(?:\d+|Manual)\s+\d+\s+([\d,]+\.\d{2})'
    return [{'invoice_date': d, 'gross_amount': v.replace(',', '')} for d, v in re.findall(pattern, text)]

def generate_dynamic_filename(earliest_date, latest_date, merchant_names):
    """Generate dynamic filename based on date range and merchant names"""
    # Format dates as DDMMYYYY
    earliest_str = earliest_date.strftime('%d%m%Y')
    latest_str = latest_date.strftime('%d%m%Y')
    
    # Clean up merchant names and remove duplicates
    unique_merchants = list(set(merchant_names))
    # Remove special characters and spaces for filename
    clean_merchants = []
    for merchant in unique_merchants:
        # Remove common suffixes
        merchant_clean = re.sub(r'\b(Service Station|Station|Connect|Lane|Brow)\b', '', merchant)
        merchant_clean = re.sub(r'[^\w\s]', '', merchant_clean).strip()
        if merchant_clean and merchant_clean not in ['Unknown', 'Number not in mapping']:
            clean_merchants.append(merchant_clean.replace(' ', '_'))
    
    # Join merchant names with underscore
    merchants_str = '_'.join(clean_merchants) if clean_merchants else 'Various'
    
    # Generate filename
    filename = f"{earliest_str}_{latest_str}_{merchants_str}.pdf"
    
    return filename

# --- MAIN PUBLIC FUNCTION ---
def process_bill(pdf_object, filename, upload_date):
    try:
        txt = _extract_text(pdf_object)
    except Exception as e:
        print(f"Error reading PDF content: {e}")
        return {"error": "Could not read or process the PDF file."}
    
    garage_numbers = re.findall(r'\*\*\*Total\s+Garage\s+(\d+)', txt)
    transaction_blocks = re.split(r'\*\*\*Total\s+Garage\s+\d+', txt)
    
    earliest_invoice_date = None
    latest_invoice_date = None
    total_gross_amount = 0.0
    all_line_items = []
    merchant_names = []
    
    for i in range(len(garage_numbers)):
        block, garage_number = transaction_blocks[i], garage_numbers[i]
        intermediate_name = GARAGE_NUMBER_TO_INTERMEDIATE_NAME.get(garage_number)
        final_merchant_name = _find_best_standard_name(intermediate_name)
        
        # Collect merchant names for filename generation
        if final_merchant_name not in merchant_names:
            merchant_names.append(final_merchant_name)
        
        batch_data_in_block = _extract_batch_data(block)
        for b in batch_data_in_block:
            current_date = datetime.strptime(b['invoice_date'], '%d.%m.%Y')
            
            all_line_items.append({
                'supplier_name': 'Allstar',
                'merchant_name': final_merchant_name,
                'garage_number': garage_number,
                'invoice_date': current_date.strftime('%Y-%m-%d'),
                'gross_amount': b['gross_amount']
            })
            
            # Track earliest and latest dates
            if earliest_invoice_date is None or current_date < earliest_invoice_date:
                earliest_invoice_date = current_date
            if latest_invoice_date is None or current_date > latest_invoice_date:
                latest_invoice_date = current_date
                
            total_gross_amount += float(b['gross_amount'])
    
    # Generate dynamic filename if we have dates
    dynamic_filename = None
    if earliest_invoice_date and latest_invoice_date:
        dynamic_filename = generate_dynamic_filename(
            earliest_invoice_date,
            latest_invoice_date,
            merchant_names
        )

    # Extract invoice/file reference number from filename if present
    invoice_reference = None
    try:
        ref_match = re.search(r"(\d{6,})", filename or "")
        if ref_match:
            invoice_reference = ref_match.group(1)
    except Exception:
        invoice_reference = None
            
    return {
        'dashboard_data': {
            'supplier_name': 'Allstar',
            'invoice_date': earliest_invoice_date.strftime('%Y-%m-%d') if earliest_invoice_date else None,
            'gross_amount': f"{total_gross_amount:.2f}",
            'dynamic_filename': dynamic_filename,  # Add this for use in main.py
            'invoice_reference': invoice_reference
        },
        'line_items': all_line_items
    }