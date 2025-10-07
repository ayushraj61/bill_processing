import os
import base64
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as GoogleRequest
import io
from datetime import datetime
import databases
import sqlalchemy

# Configuration - matches your main.py
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]
SOURCE_FOLDER_ID = '1d_uPi4CnYaS6IptjVt-xQR3uAMpvfmTi'  # New pending bills folder

# Database setup
# Prefer environment variable; fall back to LIVE database URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:AR%22%28M%28NB%28Qe%5B%22c9J@136.112.86.19:5432/postgres"
)
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Company email mapping table
company_email_mapping = sqlalchemy.Table(
    "company_email_mapping", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("company_name", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("sender_email", sqlalchemy.String, nullable=False),
)

def get_credentials():
    """Get Google credentials with both Drive and Gmail scopes"""
    creds = None
    if os.path.exists('token_email.pickle'):
        with open('token_email.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8081)  # Different port to avoid conflict
        
        with open('token_email.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def extract_email_body(payload):
    """
    Extract email body text from Gmail message payload
    """
    body = ""
    
    def extract_text_from_part(part):
        if part.get('mimeType') == 'text/plain':
            data = part.get('body', {}).get('data')
            if data:
                return base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
        elif part.get('mimeType') == 'text/html':
            data = part.get('body', {}).get('data')
            if data:
                # For HTML, we'll extract text content (basic approach)
                html_content = base64.urlsafe_b64decode(data.encode('UTF-8')).decode('UTF-8')
                # Simple HTML tag removal
                import re
                text_content = re.sub(r'<[^>]+>', '', html_content)
                return text_content
        elif part.get('mimeType') == 'multipart/alternative':
            # Handle nested multipart/alternative (text + html versions)
            nested_parts = part.get('parts', [])
            for nested_part in nested_parts:
                if nested_part.get('mimeType') == 'text/plain':
                    nested_body = extract_text_from_part(nested_part)
                    if nested_body:
                        return nested_body
                elif nested_part.get('mimeType') == 'text/html' and not body:
                    nested_body = extract_text_from_part(nested_part)
                    if nested_body:
                        body = nested_body
            return body
        return ""
    
    # Check if it's a multipart message
    if payload.get('mimeType') in ['multipart/alternative', 'multipart/mixed']:
        parts = payload.get('parts', [])
        for part in parts:
            # Skip attachment parts
            if part.get('filename'):
                continue
                
            if part.get('mimeType') == 'text/plain':
                body = extract_text_from_part(part)
                break
            elif part.get('mimeType') == 'text/html' and not body:
                body = extract_text_from_part(part)
            elif part.get('mimeType') == 'multipart/alternative':
                # Handle nested multipart/alternative
                body = extract_text_from_part(part)
                if body:
                    break
    else:
        # Single part message
        body = extract_text_from_part(payload)
    
    # Clean up the body text
    if body:
        # Extract the main message content from forwarded emails
        if 'Hello site operator' in body:
            # Find the main message content
            start_idx = body.find('Hello site operator')
            if start_idx != -1:
                # Extract from "Hello site operator" to end or signature
                main_content = body[start_idx:]
                # Remove signatures and URLs
                for sig in ['Sent from my Galaxy', 'Thanks', 'https://', 'Thanks \'n\' Regards']:
                    if sig in main_content:
                        main_content = main_content[:main_content.find(sig)]
                body = main_content
        
        # Clean up whitespace
        body = body.strip()
        # Limit length to reasonable size
        if len(body) > 1000:
            body = body[:1000] + "..."
    
    return body.strip()

async def get_company_from_recipient_email(recipient_email):
    """Get company name from recipient email using database mapping"""
    try:
        print(f"🔍 [DEBUG] Looking up company for recipient: {recipient_email}")
        await database.connect()
        print(f"🔍 [DEBUG] Database connected successfully")
        
        mapping = await database.fetch_one(
            company_email_mapping.select().where(company_email_mapping.c.sender_email == recipient_email)
        )
        print(f"🔍 [DEBUG] Query result: {mapping}")
        
        await database.disconnect()
        
        if mapping:
            print(f"✅ [DEBUG] Found company: {mapping['company_name']}")
            return mapping['company_name']
        else:
            print(f"⚠️  No company mapping found for recipient: {recipient_email}")
            return "Unknown"  # Default fallback
    except Exception as e:
        print(f"❌ Error getting company from recipient email: {e}")
        return "Unknown"

async def create_company_folder(service_drive, company_name):
    """Create Pending/Company folder structure (NO month subfolder for pending)"""
    try:
        # Get or create company folder
        company_query = f"'{SOURCE_FOLDER_ID}' in parents and name='{company_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        company_results = service_drive.files().list(q=company_query, fields="files(id)").execute()
        company_items = company_results.get('files', [])
        
        if not company_items:
            # Create company folder
            company_metadata = {
                'name': company_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [SOURCE_FOLDER_ID]
            }
            company_folder = service_drive.files().create(body=company_metadata, fields='id').execute()
            company_folder_id = company_folder.get('id')
            print(f"📁 Created company folder: {company_name}")
        else:
            company_folder_id = company_items[0].get('id')
            print(f"📁 Found company folder: {company_name}")
        
        return company_folder_id
        
    except Exception as e:
        print(f"❌ Error creating company folder: {e}")
        return SOURCE_FOLDER_ID  # Fallback to main folder

async def check_duplicate_by_invoice_reference(service_drive, pdf_data, filename):
    """
    Check if a bill is a duplicate by extracting invoice reference and comparing with database
    Returns (is_duplicate, invoice_reference) tuple
    """
    try:
        # Import the processor to extract invoice reference
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from processors.router import route_and_process_bill
        import databases
        import sqlalchemy
        from sqlalchemy import text
        
        # Process the PDF to extract invoice reference
        pdf_io = io.BytesIO(pdf_data)
        extraction_result = route_and_process_bill(pdf_io, filename, None)
        
        if extraction_result and 'dashboard_data' in extraction_result:
            # Only trust the content-extracted reference. Do NOT fallback to filename here.
            invoice_reference = extraction_result['dashboard_data'].get('invoice_reference')
            
            if invoice_reference:
                # Check database for existing bill with same reference number
                database = databases.Database(os.getenv(
                    "DATABASE_URL",
                    "postgresql://postgres:AR%22%28M%28NB%28Qe%5B%22c9J@136.112.86.19:5432/postgres"
                ))
                await database.connect()
                
                try:
                    # Check both bills and bpoil tables for the reference number
                    bills_query = text("SELECT id FROM bills WHERE invoice_reference = :ref")
                    bpoil_query = text("SELECT id FROM bpoil WHERE bill_reference_number = :ref OR invoice_reference = :ref")
                    
                    bills_result = await database.fetch_one(bills_query, {"ref": invoice_reference})
                    bpoil_result = await database.fetch_one(bpoil_query, {"ref": invoice_reference})
                    
                    if bills_result or bpoil_result:
                        print(f"    -> Found duplicate bill with reference: {invoice_reference}")
                        # Delete duplicate file from Drive
                        try:
                            # Try to find the file by name in SOURCE folder; safer to skip deletion if not found
                            # Caller can handle deletion by id after upload if desired
                            pass
                        except Exception:
                            pass
                        return True, invoice_reference
                    else:
                        print(f"    -> New bill with reference: {invoice_reference}")
                        return False, invoice_reference
                        
                finally:
                    await database.disconnect()
            else:
                # No invoice reference found - treat as new bill to be safe (leave blank)
                print(f"    -> No invoice reference found, treating as new bill")
                return False, None
        else:
            # Extraction failed - treat as new bill to be safe
            print(f"    -> Extraction failed, treating as new bill")
            return False, None
            
    except Exception as e:
        print(f"    -> Error checking invoice reference: {e}")
        # If we can't check, treat as new bill to be safe
        return False, None

def get_or_create_client_folder(service_drive, client_name):
    """
    Get or create a client-specific folder within the pending bills folder
    """
    # Search for existing client folder
    query = f"'{SOURCE_FOLDER_ID}' in parents and name='{client_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = service_drive.files().list(q=query, fields='files(id, name)').execute()
    items = results.get('files', [])
    
    if items:
        return items[0]['id']
    else:
        # Create new client folder
        folder_metadata = {
            'name': client_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [SOURCE_FOLDER_ID]
        }
        folder = service_drive.files().create(body=folder_metadata, fields='id').execute()
        print(f"Created new client folder: {client_name}")
        return folder.get('id')

async def scan_and_upload_attachments():
    """
    Scan Gmail for unread emails with PDF attachments and upload them to Google Drive
    """
    try:
        # Get credentials and build services
        creds = get_credentials()
        service_drive = build('drive', 'v3', credentials=creds)
        service_gmail = build('gmail', 'v1', credentials=creds)
        
        # Search for unread emails with attachments in the inbox
        # Company detection happens later by reading the TO field from email headers
        # You can customize this query to filter by sender or subject
        # Examples:
        # query = 'is:unread has:attachment from:bills@supplier.com'
        # query = 'is:unread has:attachment subject:invoice'
        query = 'is:unread has:attachment'
        
        results = service_gmail.users().messages().list(
            userId='me', 
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] No new unread emails with attachments found.")
            return 0
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Found {len(messages)} unread email(s) with attachments.")
        
        uploaded_count = 0
        
        for message in messages:
            # Get the full message
            msg = service_gmail.users().messages().get(
                userId='me', 
                id=message['id']
            ).execute()
            
            # Extract email metadata
            headers = msg['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            recipient_raw = next((h['value'] for h in headers if h['name'] == 'To'), 'Unknown Recipient')
            
            # Extract clean email address from TO field (e.g., "Name <email@domain.com>" -> "email@domain.com")
            import re
            recipient_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', recipient_raw)
            recipient = recipient_match.group(0) if recipient_match else recipient_raw
            
            # Extract email body text
            email_body = extract_email_body(msg['payload'])
            
            print(f"\nProcessing email from: {sender}")
            print(f"  Subject: {subject}")
            if email_body:
                print(f"  Email body: {email_body[:100]}...")
            else:
                print(f"  No email body text found")
            
            # Check for attachments
            if 'payload' in msg and 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    filename = part.get('filename', '')
                    
                    # Only process PDF files
                    if filename and filename.lower().endswith('.pdf'):
                        attachment_id = part['body'].get('attachmentId')
                        
                        if attachment_id:
                            print(f"  - Found PDF: {filename}")
                            
                            try:
                                # Download attachment
                                attachment = service_gmail.users().messages().attachments().get(
                                    userId='me',
                                    messageId=message['id'],
                                    id=attachment_id
                                ).execute()
                                
                                # Decode the attachment data
                                file_data = base64.urlsafe_b64decode(
                                    attachment['data'].encode('UTF-8')
                                )
                                
                                # Check for duplicates using invoice reference instead of filename
                                is_duplicate, invoice_reference = await check_duplicate_by_invoice_reference(
                                    service_drive, file_data, filename
                                )
                                
                                if is_duplicate:
                                    print(f"    -> Duplicate bill detected (Invoice Ref: {invoice_reference}). Skipping...")
                                    continue
                                
                                # Determine company from recipient email using database mapping
                                company_name = await get_company_from_recipient_email(recipient)
                                print(f"  📧 Recipient: {recipient} -> Company: {company_name}")
                                
                                # Create company folder structure (NO month subfolder for pending bills)
                                target_folder_id = await create_company_folder(service_drive, company_name)
                                
                                # Upload to Google Drive in company folder
                                media = MediaIoBaseUpload(
                                    io.BytesIO(file_data),
                                    mimetype='application/pdf',
                                    resumable=True
                                )
                                
                                # Prepare description with email body if available
                                description_parts = [
                                    f'Uploaded from email: {sender}',
                                    f'Recipient: {recipient}',
                                    f'Subject: {subject}',
                                    f'Company: {company_name}'
                                ]
                                if email_body:
                                    description_parts.append(f'Email Body: {email_body}')
                                
                                file_metadata = {
                                    'name': filename,
                                    'parents': [target_folder_id],
                                    'description': ' | '.join(description_parts)
                                }
                                
                                uploaded_file = service_drive.files().create(
                                    body=file_metadata,
                                    media_body=media,
                                    fields='id, name'
                                ).execute()
                                
                                print(f"    -> Successfully uploaded '{filename}' to {company_name} folder")
                                print(f"       File ID: {uploaded_file.get('id')}")
                                uploaded_count += 1
                                
                                # Mark email as read
                                service_gmail.users().messages().modify(
                                    userId='me',
                                    id=message['id'],
                                    body={'removeLabelIds': ['UNREAD']}
                                ).execute()
                                print(f"    -> Marked email as read")
                                
                            except Exception as e:
                                print(f"    ERROR: Failed to process {filename}: {str(e)}")
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Summary: Uploaded {uploaded_count} new PDF(s) to Google Drive")
        return uploaded_count
        
    except Exception as e:
        print(f"\n[ERROR] An error occurred: {str(e)}")
        print("Please check:")
        print("1. credentials.json file exists")
        print("2. Gmail API is enabled in Google Cloud Console")
        print("3. You have the necessary permissions")
        return -1

def scan_with_filter(sender_filter=None, subject_filter=None, days_back=7):
    """
    Advanced scanning with filters
    
    Args:
        sender_filter: Email address or domain to filter by
        subject_filter: Keywords to search in subject
        days_back: Number of days to look back for emails
    """
    try:
        creds = get_credentials()
        service_drive = build('drive', 'v3', credentials=creds)
        service_gmail = build('gmail', 'v1', credentials=creds)
        
        # Build query with filters
        query_parts = ['has:attachment', 'filename:pdf']
        
        if sender_filter:
            query_parts.append(f'from:{sender_filter}')
        
        if subject_filter:
            query_parts.append(f'subject:{subject_filter}')
        
        # Add date filter
        from datetime import datetime, timedelta
        date_after = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
        query_parts.append(f'after:{date_after}')
        
        query = ' '.join(query_parts)
        print(f"Search query: {query}")
        
        results = service_gmail.users().messages().list(
            userId='me',
            q=query
        ).execute()
        
        messages = results.get('messages', [])
        print(f"Found {len(messages)} matching email(s)")
        
        # Process messages (same as scan_and_upload_attachments)
        # ... (rest of the processing logic)
        
    except Exception as e:
        print(f"Error in scan_with_filter: {str(e)}")

if __name__ == '__main__':
    # Run the scanner
    print("=" * 60)
    print("AUTOMATED EMAIL ATTACHMENT SCANNER")
    print("=" * 60)
    
    # Basic scan for all unread emails with attachments
    import asyncio
    result = asyncio.run(scan_and_upload_attachments())
    
    # Example of using filters (uncomment to use):
    # scan_with_filter(
    #     sender_filter="accounting@company.com",
    #     subject_filter="invoice",
    #     days_back=30
    # )
    
    if result >= 0:
        print("\nScan completed successfully!")
        if result > 0:
            print(f"You can now process the {result} new bill(s) from the dashboard.")
    else:
        print("\nScan failed. Please check the error messages above.")