#!/usr/bin/env python3
"""
Automated Bill Processing Pipeline
This script:
1. Scans Gmail for PDF attachments
2. Uploads them to Google Drive pending folder
3. Processes them through the bill extraction system
4. Can be scheduled to run automatically via cron or Windows Task Scheduler
"""

import os
import sys
import time
import schedule
import logging
from datetime import datetime
from email_scanner import scan_and_upload_attachments, get_credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
import asyncio
import databases
from processors.router import route_and_process_bill

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('automation.log'),
        logging.StreamHandler()
    ]
)

# Configuration
DATABASE_URL = "postgresql://bill_user:ayush23854@localhost/bill_processor_db"
SOURCE_FOLDER_ID = '14h9shWD28VqgcCKluwbwnGuHpB0f5ZdT'

async def process_new_bills():
    """
    Process any new bills in the Google Drive folder that aren't in the database yet
    """
    try:
        logging.info("Starting bill processing...")
        
        # Connect to database
        database = databases.Database(DATABASE_URL)
        await database.connect()
        
        # Get Google Drive service
        creds = get_credentials()
        service = build('drive', 'v3', credentials=creds)
        
        # Query for PDF files in source folder and all client subfolders
        # First get all client folders
        folder_query = f"'{SOURCE_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        folder_results = service.files().list(
            q=folder_query,
            fields="files(id, name)"
        ).execute()
        
        client_folders = folder_results.get('files', [])
        logging.info(f"Found {len(client_folders)} client folders")
        
        # Get all PDF files from main folder and client folders
        all_files = []
        
        # Check main folder for PDFs
        main_query = f"'{SOURCE_FOLDER_ID}' in parents and mimeType='application/pdf' and trashed=false"
        main_results = service.files().list(
            q=main_query,
            pageSize=100,
            fields="files(id, name, webViewLink, createdTime, parents)"
        ).execute()
        all_files.extend(main_results.get('files', []))
        
        # Check each client folder for PDFs
        for folder in client_folders:
            folder_query = f"'{folder['id']}' in parents and mimeType='application/pdf' and trashed=false"
            folder_results = service.files().list(
                q=folder_query,
                pageSize=100,
                fields="files(id, name, webViewLink, createdTime, parents)"
            ).execute()
            all_files.extend(folder_results.get('files', []))
        
        files_in_drive = all_files
        logging.info(f"Found {len(files_in_drive)} PDF files across all folders")
        
        processed_count = 0
        
        for file in files_in_drive:
            # Check if file already processed
            query = f"SELECT id FROM bills WHERE drive_file_id = '{file['id']}'"
            existing = await database.fetch_one(query)
            
            if not existing:
                logging.info(f"Processing new file: {file['name']}")
                
                try:
                    # Download file content
                    request = service.files().get_media(fileId=file['id'])
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                    
                    fh.seek(0)
                    
                    # Process the bill
                    extraction_result = route_and_process_bill(
                        fh, 
                        file['name'], 
                        file['createdTime']
                    )
                    
                    dashboard_data = extraction_result.get('dashboard_data', {})
                    line_items = extraction_result.get('line_items', [])
                    
                    # Get dynamic filename
                    dynamic_filename = dashboard_data.get('dynamic_filename')
                    filename_to_store = dynamic_filename if dynamic_filename else file['name']
                    
                    # Parse dates
                    from datetime import date, datetime as dt
                    invoice_date_str = dashboard_data.get('invoice_date')
                    invoice_date_obj = date.fromisoformat(invoice_date_str) if invoice_date_str else None
                    upload_date = dt.fromisoformat(file['createdTime'].replace("Z", "+00:00"))
                    
                    # Insert into database
                    insert_query = """
                        INSERT INTO bills (
                            id, drive_file_id, filename, upload_date, 
                            status, supplier_name, invoice_date, 
                            gross_amount, extracted_data
                        ) VALUES (
                            :id, :drive_file_id, :filename, :upload_date,
                            :status, :supplier_name, :invoice_date,
                            :gross_amount, :extracted_data
                        )
                    """
                    
                    await database.execute(insert_query, {
                        'id': file['id'],
                        'drive_file_id': file['id'],
                        'filename': filename_to_store,
                        'upload_date': upload_date,
                        'status': 'Pending',
                        'supplier_name': dashboard_data.get('supplier_name'),
                        'invoice_date': invoice_date_obj,
                        'gross_amount': dashboard_data.get('gross_amount'),
                        'extracted_data': line_items
                    })
                    
                    processed_count += 1
                    logging.info(f"  ✓ Successfully processed: {filename_to_store}")
                    
                except Exception as e:
                    logging.error(f"  ✗ Failed to process {file['name']}: {str(e)}")
        
        await database.disconnect()
        
        logging.info(f"Bill processing complete. Processed {processed_count} new bills.")
        return processed_count
        
    except Exception as e:
        logging.error(f"Error in process_new_bills: {str(e)}")
        return -1

def run_complete_pipeline():
    """
    Run the complete automation pipeline:
    1. Scan emails for attachments
    2. Upload to Google Drive
    3. Process bills and store in database
    """
    print("\n" + "="*60)
    print(f"AUTOMATED PIPELINE RUN - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Step 1: Scan emails and upload attachments
    logging.info("Step 1: Scanning emails for PDF attachments...")
    uploaded_count = scan_and_upload_attachments()
    
    if uploaded_count > 0:
        # Wait a moment for Drive to sync
        time.sleep(2)
        
        # Step 2: Process new bills
        logging.info(f"Step 2: Processing {uploaded_count} new files...")
        processed_count = asyncio.run(process_new_bills())
        
        if processed_count > 0:
            logging.info(f"✓ Pipeline complete! Processed {processed_count} new bills.")
        else:
            logging.info("No new bills to process.")
    else:
        logging.info("No new attachments found in emails.")
    
    print("="*60 + "\n")

def schedule_automation():
    """
    Schedule the automation to run at specific times
    """
    # Run every 5 minutes
    schedule.every(5).minutes.do(run_complete_pipeline)
    
    logging.info("Automation scheduled. Press Ctrl+C to stop.")
    logging.info("Schedule:")
    logging.info("- Scanning emails every 5 minutes")
    logging.info("- Processing and uploading any new bills found")
    
    # Run immediately on start
    run_complete_pipeline()
    
    while True:
        schedule.run_pending()
        time.sleep(30)  # Check every 30 seconds

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Bill Processing Pipeline')
    parser.add_argument(
        '--mode',
        choices=['once', 'scheduled', 'email-only', 'process-only'],
        default='once',
        help='Run mode: once (single run), scheduled (continuous), email-only, or process-only'
    )
    parser.add_argument(
        '--sender',
        type=str,
        help='Filter emails by sender (e.g., bills@supplier.com)'
    )
    parser.add_argument(
        '--subject',
        type=str,
        help='Filter emails by subject keywords'
    )
    
    args = parser.parse_args()
    
    if args.mode == 'once':
        # Single run of the complete pipeline
        run_complete_pipeline()
        
    elif args.mode == 'scheduled':
        # Run on schedule
        try:
            schedule_automation()
        except KeyboardInterrupt:
            logging.info("\nScheduled automation stopped by user.")
            
    elif args.mode == 'email-only':
        # Only scan and upload emails
        from email_scanner import scan_with_filter
        if args.sender or args.subject:
            scan_with_filter(
                sender_filter=args.sender,
                subject_filter=args.subject
            )
        else:
            scan_and_upload_attachments()
            
    elif args.mode == 'process-only':
        # Only process bills already in Drive
        asyncio.run(process_new_bills())