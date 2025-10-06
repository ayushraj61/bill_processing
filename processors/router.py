# router.py
import pdfplumber
from . import allstar_processor
from . import bpoil_extracter
from . import other_processor

def route_and_process_bill(pdf_object, filename, upload_date):
    """
    Identify the supplier from the PDF text and call the correct processor.
    pdf_object: file-like object (e.g. BytesIO) that will also be passed
                to the supplier processor, so its pointer must be reset.
    """
    text = ""
    try:
        # Always rewind before reading
        if hasattr(pdf_object, "seek"):
            pdf_object.seek(0)

        # Extract first-page text for routing
        with pdfplumber.open(pdf_object) as pdf:
            if pdf.pages:
                text = pdf.pages[0].extract_text() or ""
    except Exception as e:
        print(f"Could not read PDF for routing: {e}")
        return {"error": "Invalid PDF file."}

    # VERY IMPORTANT: reset pointer so downstream processors
    # can read the entire PDF again.
    if hasattr(pdf_object, "seek"):
        pdf_object.seek(0)

    # --- Routing Logic ---
    lower_text = text.lower()

    # Detect BP Oil UK Limited invoices via vendor name only
    if "bp oil uk limited" in lower_text:
        print("Routing to: BP Oil Extracter")
        return bpoil_extracter.process_bill(pdf_object, filename, upload_date)

    if "allstar" in lower_text:
        print("Routing to: Allstar Processor")
        return allstar_processor.process_bill(pdf_object, filename, upload_date)

    # Add more suppliers here as elif blocks when needed.
    # elif "shell" in text.lower():
    #     return shell_processor.process_bill(pdf_object, filename, upload_date)

    print("Routing to: Other (generic) processor")
    return other_processor.process_bill(pdf_object, filename, upload_date)