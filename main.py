import os, io, json, pickle, uvicorn, re
from collections import OrderedDict
from fastapi import FastAPI, Request, HTTPException, UploadFile, File, Form, BackgroundTasks, Cookie, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request as GoogleRequest
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from processors.router import route_and_process_bill
import databases
import sqlalchemy
from datetime import date, datetime, timezone
from decimal import Decimal
import traceback
import asyncio
import hashlib
import secrets
import string

# --- Database Configuration ---
DATABASE_URL = "postgresql://postgres:AR%22%28M%28NB%28Qe%5B%22c9J@136.112.86.19:5432/postgres"
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

# Main bills table
bills = sqlalchemy.Table(
    "bills", metadata,
    sqlalchemy.Column("id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("drive_file_id", sqlalchemy.String),
    sqlalchemy.Column("invoice_reference", sqlalchemy.String),
    sqlalchemy.Column("filename", sqlalchemy.String),
    sqlalchemy.Column("supplier_name", sqlalchemy.String),
    sqlalchemy.Column("upload_date", sqlalchemy.DateTime(timezone=True)),  # Explicitly timezone-aware
    sqlalchemy.Column("invoice_date", sqlalchemy.Date),
    sqlalchemy.Column("gross_amount", sqlalchemy.Numeric(10, 2)),
    sqlalchemy.Column("status", sqlalchemy.String),
    sqlalchemy.Column("extracted_data", sqlalchemy.JSON),
    sqlalchemy.Column("email_text", sqlalchemy.Text),
    sqlalchemy.Column("web_view_link", sqlalchemy.String),  # Store Google Drive preview link
)

# BP Oil and Other bills table (each line item gets its own row)
bpoil = sqlalchemy.Table(
    "bpoil", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("drive_file_id", sqlalchemy.String),  # References the Google Drive file
    sqlalchemy.Column("invoice_reference", sqlalchemy.String),
    sqlalchemy.Column("bill_reference_number", sqlalchemy.String),
    sqlalchemy.Column("filename", sqlalchemy.String),
    sqlalchemy.Column("supplier_name", sqlalchemy.String),
    sqlalchemy.Column("upload_date", sqlalchemy.DateTime(timezone=True)),  # Explicitly timezone-aware
    sqlalchemy.Column("invoice_date", sqlalchemy.Date),
    sqlalchemy.Column("gross_amount", sqlalchemy.Numeric(10, 2)),
    sqlalchemy.Column("status", sqlalchemy.String),
    sqlalchemy.Column("extracted_data", sqlalchemy.JSON),
    sqlalchemy.Column("email_text", sqlalchemy.Text),
    sqlalchemy.Column("web_view_link", sqlalchemy.String),  # Store Google Drive preview link
    # Line item columns for detailed breakdown
    sqlalchemy.Column("type", sqlalchemy.String),
    sqlalchemy.Column("a_c", sqlalchemy.String),
    sqlalchemy.Column("date", sqlalchemy.Date),
    sqlalchemy.Column("ref", sqlalchemy.String),
    sqlalchemy.Column("ex_ref", sqlalchemy.String),
    sqlalchemy.Column("n_c", sqlalchemy.String),
    sqlalchemy.Column("dept", sqlalchemy.String),
    sqlalchemy.Column("details", sqlalchemy.String),
    sqlalchemy.Column("net", sqlalchemy.Numeric(10, 2)),
    sqlalchemy.Column("t_c", sqlalchemy.String),
    sqlalchemy.Column("vat", sqlalchemy.Numeric(10, 2)),
)

# Site mappings table for BP Oil
site_mappings = sqlalchemy.Table(
    "site_mappings", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("site_name", sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column("dept", sqlalchemy.String),
    sqlalchemy.Column("short_code", sqlalchemy.String),  # For Details field (3-letter code)
    sqlalchemy.Column("company", sqlalchemy.String),
    sqlalchemy.Column("post_code", sqlalchemy.String),
)

# Nominal Code mappings table for Other processor
nominal_code = sqlalchemy.Table(
    "nominal_code", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("code", sqlalchemy.String, unique=True, nullable=False),  # N/C code like '0010', '0020'
    sqlalchemy.Column("object_name", sqlalchemy.String, nullable=False),  # Category name for AI matching
)

# Company to sender email mapping table
company_email_mapping = sqlalchemy.Table(
    "company_email_mapping", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("company_name", sqlalchemy.String, unique=True, nullable=False),  # "PRL", "Allstar"
    sqlalchemy.Column("sender_email", sqlalchemy.String, unique=True, nullable=False),  # "invoices@prl.com"
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
)

# Users table (admin + regular users)
users = sqlalchemy.Table(
    "users", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("email", sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column("password_hash", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("role", sqlalchemy.String, nullable=False),  # "admin" or "user"
    sqlalchemy.Column("accessible_companies", sqlalchemy.JSON),  # ["PRL", "Allstar"]
    sqlalchemy.Column("is_active", sqlalchemy.Boolean, default=True),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    sqlalchemy.Column("created_by", sqlalchemy.String),  # Email of admin who created this user
)

# User sessions table (permanent login storage)
user_sessions = sqlalchemy.Table(
    "user_sessions", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("user_email", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("session_token", sqlalchemy.String, unique=True, nullable=False),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    sqlalchemy.Column("last_activity", sqlalchemy.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    sqlalchemy.Column("ip_address", sqlalchemy.String),
    sqlalchemy.Column("is_active", sqlalchemy.Boolean, default=True),
)

# Audit log table (track all user actions)
audit_log = sqlalchemy.Table(
    "audit_log", metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("user_email", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("action_type", sqlalchemy.String, nullable=False),  # "login", "logout", "approve_bill", "view_bill"
    sqlalchemy.Column("bill_id", sqlalchemy.String),
    sqlalchemy.Column("company_name", sqlalchemy.String),
    sqlalchemy.Column("timestamp", sqlalchemy.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)),
    sqlalchemy.Column("ip_address", sqlalchemy.String),
    sqlalchemy.Column("details", sqlalchemy.JSON),  # Extra info like bill filename, etc.
)

engine = sqlalchemy.create_engine(DATABASE_URL)
metadata.create_all(engine)

# --- Authentication Helper Functions ---
def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == password_hash

def generate_random_password(length: int = 12) -> str:
    """Generate secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(secrets.choice(characters) for _ in range(length))

def generate_session_token() -> str:
    """Generate unique session token"""
    return secrets.token_urlsafe(32)

async def get_current_user(session_token: str = None):
    """Get current user from session token"""
    if not session_token:
        return None
    
    session = await database.fetch_one(
        user_sessions.select().where(
            (user_sessions.c.session_token == session_token) & 
            (user_sessions.c.is_active == True)
        )
    )
    
    if not session:
        return None
    
    user = await database.fetch_one(
        users.select().where(
            (users.c.email == session['user_email']) &
            (users.c.is_active == True)
        )
    )
    
    return user

async def log_user_action(user_email: str, action_type: str, ip_address: str = None, 
                         bill_id: str = None, company_name: str = None, details: dict = None):
    """Log user action to audit_log"""
    try:
        await database.execute(
            audit_log.insert().values(
                user_email=user_email,
                action_type=action_type,
                bill_id=bill_id,
                company_name=company_name,
                timestamp=datetime.now(timezone.utc),
                ip_address=ip_address,
                details=details
            )
        )
    except Exception as e:
        print(f"Error logging action: {e}")

async def send_password_email(to_email: str, password: str):
    """Send password to user via Gmail OAuth"""
    try:
        # Get Gmail service using OAuth
        creds = None
        if os.path.exists('token_email.pickle'):
            with open('token_email.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        # Add gmail.send scope if not present
        GMAIL_SCOPES = [
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify'
        ]
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(GoogleRequest())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', GMAIL_SCOPES)
                creds = flow.run_local_server(port=8081)
            
            with open('token_email.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Create email message
        import base64
        from email.mime.text import MIMEText
        
        message_text = f"""
        Hello,

        Your new password for the Bill Processing System is:

        {password}

        Please login at: http://127.0.0.1:8000/login

        Keep this password safe. You can change it after logging in.

        Best regards,
        Bill Processing System
        """
        
        message = MIMEText(message_text)
        message['to'] = to_email
        message['from'] = 'ayush23854@gmail.com'
        message['subject'] = 'Your New Password - Bill Processing System'
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_message = {'raw': raw_message}
        
        service.users().messages().send(userId='me', body=send_message).execute()
        print(f"✅ Password email sent to {to_email}")
        
    except Exception as e:
        print(f"Email sending failed: {e}")
        raise  # Re-raise so caller knows it failed

def reorder_dict_keys(data_dict, key_order):
    """Reorder dictionary keys according to the specified order"""
    if not isinstance(data_dict, dict):
        return data_dict
    
    ordered_dict = OrderedDict()
    # Add keys in the specified order
    for key in key_order:
        if key in data_dict:
            ordered_dict[key] = data_dict[key]
    
    # Add any remaining keys that weren't in the order
    for key, value in data_dict.items():
        if key not in ordered_dict:
            ordered_dict[key] = value
    
    return ordered_dict

# --- FastAPI App ---
app = FastAPI()
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
async def startup():
    await database.connect()
    print("✓ Database connected successfully")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected")

# --- Google Configuration ---
SCOPES = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets'
]
SOURCE_FOLDER_ID = '14h9shWD28VqgcCKluwbwnGuHpB0f5ZdT'
DESTINATION_PARENT_FOLDER_ID = '1qGaIEOfv2t7ZtcbNDNkPO8kieOItMvux'

# BP Oil Sheets Configuration
UNIVERSAL_APPROVED_SHEET_ID = '1WuUAvf9fZzcfjdkWXVG9ASDdF7oaz_b3dSNp7Cm4tMw'
UNIVERSAL_APPROVED_TAB = 'Sheet1'

def get_drive_service():
    """Get Google Drive service with proper authentication"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('drive', 'v3', credentials=creds)

def extract_email_body_from_description(description):
    """Extract email body text from Drive file description"""
    if not description:
        return ""
    
    # Look for "Email Body:" in the description
    if "Email Body:" in description:
        parts = description.split("Email Body:")
        if len(parts) > 1:
            email_body = parts[1].strip()
            # Remove any trailing metadata
            if " | " in email_body:
                email_body = email_body.split(" | ")[0]
            return email_body
    
    return ""

def get_sheets_service():
    """Get Google Sheets service"""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GoogleRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('sheets', 'v4', credentials=creds)

def append_bpoil_rows_to_sheet(spreadsheet_id: str, rows: list[dict]):
    """Append BP Oil rows to Google Sheet"""
    if not rows:
        return
    
    try:
        sheets = get_sheets_service()
        headers = ['Type','A/C','Date','Ref','Ex.Ref','N/C','Dept','Details','Net','T/C','VAT']
        
        # Check if headers exist
        range_a1 = f'{UNIVERSAL_APPROVED_TAB}!1:1'
        resp = sheets.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=range_a1,
            majorDimension='ROWS'
        ).execute()
        
        first_row = resp.get('values', [])
        if not first_row:
            sheets.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_a1,
                valueInputOption='USER_ENTERED',
                body={'values': [headers]}
            ).execute()
        
        # Prepare data rows
        values = []
        for r in rows:
            values.append([
                r.get('Type'), r.get('A/C'), r.get('Date'), r.get('Ref'), r.get('Ex.Ref'),
                r.get('N/C'), r.get('Dept'), r.get('Details'), r.get('Net'), r.get('T/C'), r.get('VAT')
            ])
        
        # Append data
        sheets.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=f'{UNIVERSAL_APPROVED_TAB}!A1',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': values}
        ).execute()
        
        print(f"✓ Successfully appended {len(rows)} rows to Google Sheet")
        
    except Exception as e:
        print(f"[Sheets] Error appending data: {e}")

# --- API Endpoints for Site Mappings ---
@app.post("/api/site-mappings")
async def create_site_mapping(data: dict):
    """Create or update site mapping"""
    try:
        site_name = data.get('site_name')
        if not site_name:
            return JSONResponse(content={"error": "site_name is required"}, status_code=400)
        
        # Check if exists
        existing = await database.fetch_one(
            site_mappings.select().where(site_mappings.c.site_name == site_name)
        )
        
        if existing:
            # Update
            await database.execute(
                site_mappings.update()
                .where(site_mappings.c.site_name == site_name)
                .values(
                    dept=data.get('dept'),
                    ac_code=data.get('ac_code'),
                    short_code=data.get('short_code'),
                    updated_at=datetime.now()
                )
            )
        else:
            # Insert
            await database.execute(
                site_mappings.insert().values(
                    site_name=site_name,
                    dept=data.get('dept'),
                    ac_code=data.get('ac_code'),
                    short_code=data.get('short_code')
                )
            )
        
        return JSONResponse(content={"success": True})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/api/site-mappings")
async def get_site_mappings():
    """Get all site mappings for BP Oil extractor to use"""
    try:
        mappings = await database.fetch_all(site_mappings.select())
        result = []
        for m in mappings:
            result.append({
                'site_name': m['site_name'],
                'dept': m['dept'],
                'ac_code': m['ac_code'],
                'short_code': m['short_code']
            })
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

# Global variable to track background processing status
processing_status = {
    "is_processing": False,
    "new_files_count": 0,
    "processed_count": 0,
    "current_file": None
}

# Background task to process new files
async def process_new_files_background():
    """Process new files from Google Drive in the background"""
    global processing_status
    
    try:
        processing_status["is_processing"] = True
        processing_status["new_files_count"] = 0
        processing_status["processed_count"] = 0
        
        print("\n🔄 [BACKGROUND] Starting background file processing...")
        service = get_drive_service()

        # Client folders
        folder_query = f"'{SOURCE_FOLDER_ID}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
        folder_results = service.files().list(q=folder_query, fields="files(id, name)").execute()
        client_folders = folder_results.get('files', [])

        # PDFs in main folder
        main_query = f"'{SOURCE_FOLDER_ID}' in parents and mimeType='application/pdf' and trashed=false"
        main_results = service.files().list(
            q=main_query,
            pageSize=100,
            fields="files(id, name, webViewLink, createdTime, parents, description)"
        ).execute()
        all_files = main_results.get('files', [])

        # PDFs in client folders
        for folder in client_folders:
            sub_query = f"'{folder['id']}' in parents and mimeType='application/pdf' and trashed=false"
            sub_results = service.files().list(
                q=sub_query,
                pageSize=100,
                fields="files(id, name, webViewLink, createdTime, parents, description)"
            ).execute()
            all_files.extend(sub_results.get('files', []))

        new_files_count = 0
        
        # Process each file one by one
        for f in all_files:
            # Check if file already exists in bills table
            existing_bill = await database.fetch_one(bills.select().where(bills.c.drive_file_id == f['id']))
            if existing_bill:
                print(f"✓ File {f['name']} already in database (bills table), skipping")
                continue

            # Check if file already exists in bpoil table
            existing_bpoil = await database.fetch_one(bpoil.select().where(bpoil.c.drive_file_id == f['id']))
            if existing_bpoil:
                print(f"✓ File {f['name']} already in database (bpoil table), skipping")
                continue
            
            # File is new - process it
            new_files_count += 1
            processing_status["new_files_count"] = new_files_count
            processing_status["current_file"] = f['name']
            
            print(f"⚙ [{new_files_count}] Processing new file: {f['name']}")

            try:
                email_body = extract_email_body_from_description(f.get('description', ''))

                # Download
                req = service.files().get_media(fileId=f['id'])
                fh = io.BytesIO()
                MediaIoBaseDownload(fh, req).next_chunk()
                fh.seek(0)

                # Extract
                extraction_result = route_and_process_bill(fh, f['name'], f['createdTime'])
                dashboard_data = extraction_result.get('dashboard_data', {})
                line_items = extraction_result.get('line_items', [])
                invoice_date_str = dashboard_data.get('invoice_date')
                invoice_date_obj = date.fromisoformat(invoice_date_str) if invoice_date_str else None
                filename_to_store = dashboard_data.get('dynamic_filename') or f['name']
                invoice_ref_final = dashboard_data.get('invoice_reference') or None

                supplier_lower = (dashboard_data.get('supplier_name') or '').lower()
                if supplier_lower == 'allstar':
                    await database.execute(bills.insert().values(
                        id=f['id'],
                        drive_file_id=f['id'],
                        invoice_reference=invoice_ref_final,
                        filename=filename_to_store,
                        upload_date=datetime.fromisoformat(f['createdTime'].replace("Z", "+00:00")),
                        status='Pending',
                        supplier_name=dashboard_data.get('supplier_name'),
                        invoice_date=invoice_date_obj,
                        gross_amount=dashboard_data.get('gross_amount'),
                        extracted_data=line_items,
                        email_text=email_body,
                        web_view_link=f.get('webViewLink', '')
                    ))
                else:
                    for row in (line_items or []):
                        row_date = date.fromisoformat(row.get('Date')) if row.get('Date') else None
                        await database.execute(bpoil.insert().values(
                            drive_file_id=f['id'],
                            invoice_reference=invoice_ref_final,
                            bill_reference_number=invoice_ref_final,
                            filename=filename_to_store,
                            upload_date=datetime.fromisoformat(f['createdTime'].replace("Z", "+00:00")),
                            status='Pending',
                            supplier_name=dashboard_data.get('supplier_name'),
                            invoice_date=invoice_date_obj,
                            gross_amount=dashboard_data.get('gross_amount'),
                            extracted_data=line_items,
                            email_text=email_body,
                            web_view_link=f.get('webViewLink', ''),
                            type=row.get('Type'), a_c=row.get('A/C'), date=row_date,
                            ref=row.get('Ref'), ex_ref=row.get('Ex.Ref'), n_c=row.get('N/C'),
                            dept=row.get('Dept'), details=row.get('Details'),
                            net=row.get('Net'), t_c=row.get('T/C'), vat=row.get('VAT')
                        ))
                
                processing_status["processed_count"] += 1
                print(f"✅ [{new_files_count}] Successfully processed: {f['name']}")
                
            except Exception as e:
                print(f"✗ [{new_files_count}] Error processing file {f['name']}: {e}")
                traceback.print_exc()
        
        if new_files_count == 0:
            print("✓ [BACKGROUND] No new files to process")
        else:
            print(f"✅ [BACKGROUND] Completed! Processed {new_files_count} new file(s)\n")
            
    except Exception as e:
        print(f"✗ [BACKGROUND] Background processing error: {e}")
        traceback.print_exc()
    finally:
        # Reset processing status
        processing_status["is_processing"] = False
        processing_status["current_file"] = None

# --- Authentication Endpoints ---
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Show login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, response: Response):
    """Handle login"""
    try:
        data = await request.json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return JSONResponse(content={"error": "Email and password required"}, status_code=400)
        
        # Find user
        user = await database.fetch_one(
            users.select().where((users.c.email == email) & (users.c.is_active == True))
        )
        
        if not user or not verify_password(password, user['password_hash']):
            return JSONResponse(content={"error": "Invalid email or password"}, status_code=401)
        
        # Create session
        session_token = generate_session_token()
        client_ip = request.client.host if request.client else None
        
        await database.execute(
            user_sessions.insert().values(
                user_email=email,
                session_token=session_token,
                ip_address=client_ip,
                is_active=True
            )
        )
        
        # Log login action
        await log_user_action(email, "login", client_ip)
        
        # Set session cookie
        response = JSONResponse(content={"success": True, "role": user['role']})
        response.set_cookie(
            key="session_token",
            value=session_token,
            httponly=True,
            max_age=30*24*60*60,  # 30 days
            samesite="lax"
        )
        
        return response
        
    except Exception as e:
        print(f"Login error: {e}")
        traceback.print_exc()
        return JSONResponse(content={"error": "Login failed"}, status_code=500)

@app.post("/logout")
async def logout(request: Request, session_token: str = Cookie(None)):
    """Handle logout"""
    try:
        if session_token:
            # Deactivate session
            await database.execute(
                user_sessions.update()
                .where(user_sessions.c.session_token == session_token)
                .values(is_active=False)
            )
            
            # Get user email for logging
            session = await database.fetch_one(
                user_sessions.select().where(user_sessions.c.session_token == session_token)
            )
            if session:
                client_ip = request.client.host if request.client else None
                await log_user_action(session['user_email'], "logout", client_ip)
        
        response = JSONResponse(content={"success": True})
        response.delete_cookie("session_token")
        return response
        
    except Exception as e:
        print(f"Logout error: {e}")
        return JSONResponse(content={"error": "Logout failed"}, status_code=500)

# --- Admin Panel Endpoints ---
@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request, session_token: str = Cookie(None)):
    """Admin panel page - Admin ONLY, NO bills dashboard access"""
    user = await get_current_user(session_token)
    
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Only admins can access admin panel
    if user['role'] != 'admin':
        return RedirectResponse(url="/dashboard", status_code=303)
    
    return templates.TemplateResponse("admin.html", {"request": request, "user_email": user['email']})

@app.post("/forgot-password")
async def forgot_password(request: Request):
    """Handle forgot password - generates new password and emails to user"""
    try:
        data = await request.json()
        email = data.get('email')
        
        if not email:
            return JSONResponse(content={"error": "Email required"}, status_code=400)
        
        # Find user
        user = await database.fetch_one(
            users.select().where((users.c.email == email) & (users.c.is_active == True))
        )
        
        if not user:
            # Don't reveal if user exists or not (security)
            return JSONResponse(content={"success": True, "message": "If the email exists, a new password has been sent"})
        
        # Don't allow password reset for admin accounts (security)
        if user['role'] == 'admin':
            return JSONResponse(content={"error": "Admin passwords cannot be reset this way"}, status_code=403)
        
        # Generate new password
        new_password = generate_random_password()
        password_hash = hash_password(new_password)
        
        # Update password in database
        await database.execute(
            users.update()
            .where(users.c.email == email)
            .values(password_hash=password_hash)
        )
        
        # Invalidate all existing sessions for this user
        await database.execute(
            user_sessions.update()
            .where(user_sessions.c.user_email == email)
            .values(is_active=False)
        )
        
        # Log action
        client_ip = request.client.host if request.client else None
        await log_user_action(email, "password_reset", client_ip)
        
        # Send new password via Gmail OAuth
        try:
            await send_password_email(email, new_password)
            return JSONResponse(content={"success": True, "message": "New password sent to your email"})
        except Exception as email_error:
            print(f"Failed to send email: {email_error}")
            # Email failed - return password in response (fallback)
            return JSONResponse(content={
                "success": True, 
                "message": "Email service unavailable",
                "password": new_password,
                "note": "Please save this password"
            })
        
    except Exception as e:
        print(f"Forgot password error: {e}")
        traceback.print_exc()
        return JSONResponse(content={"error": "Password reset failed"}, status_code=500)

@app.post("/admin/create-user")
async def create_user(request: Request, session_token: str = Cookie(None)):
    """Create new user (admin only)"""
    try:
        admin = await get_current_user(session_token)
        if not admin or admin['role'] != 'admin':
            return JSONResponse(content={"error": "Unauthorized"}, status_code=403)
        
        data = await request.json()
        email = data.get('email')
        accessible_companies = data.get('accessible_companies', [])
        role = data.get('role', 'user')
        
        if not email:
            return JSONResponse(content={"error": "Email required"}, status_code=400)
        
        # Check if user exists
        existing = await database.fetch_one(users.select().where(users.c.email == email))
        if existing:
            return JSONResponse(content={"error": "User already exists"}, status_code=400)
        
        # Generate random password
        password = generate_random_password()
        password_hash = hash_password(password)
        
        # Create user
        await database.execute(
            users.insert().values(
                email=email,
                password_hash=password_hash,
                role=role,
                accessible_companies=accessible_companies,
                is_active=True,
                created_by=admin['email']
            )
        )
        
        # Log action
        client_ip = request.client.host if request.client else None
        await log_user_action(admin['email'], "create_user", client_ip, details={"new_user": email})
        
        # Send email with password using Gmail OAuth
        email_sent = False
        try:
            await send_password_email(email, password)
            email_sent = True
            print(f"✅ Credentials emailed to {email}")
        except Exception as email_error:
            print(f"⚠️ Failed to email credentials: {email_error}")
            # Will show password to admin as fallback
        
        # Return password to admin (for display and manual sharing if email failed)
        return JSONResponse(content={
            "success": True, 
            "password": password,
            "email_sent": email_sent
        })
        
    except Exception as e:
        print(f"Error creating user: {e}")
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/admin/users")
async def get_users(session_token: str = Cookie(None)):
    """Get all users (admin only)"""
    try:
        admin = await get_current_user(session_token)
        if not admin or admin['role'] != 'admin':
            return JSONResponse(content={"error": "Unauthorized"}, status_code=403)
        
        all_users = await database.fetch_all(users.select().where(users.c.is_active == True).order_by(users.c.created_at.desc()))
        
        result = []
        for u in all_users:
            result.append({
                'email': u['email'],
                'role': u['role'],
                'accessible_companies': u['accessible_companies'],
                'created_at': u['created_at'].isoformat() if u['created_at'] else None,
                'created_by': u['created_by'],
                'is_active': u['is_active']
            })
        
        return JSONResponse(content=result)
        
    except Exception as e:
        print(f"Error fetching users: {e}")
        return JSONResponse(content=[], status_code=500)

@app.post("/admin/delete-user")
async def delete_user(request: Request, session_token: str = Cookie(None)):
    """Delete user (admin only)"""
    try:
        admin = await get_current_user(session_token)
        if not admin or admin['role'] != 'admin':
            return JSONResponse(content={"error": "Unauthorized"}, status_code=403)
        
        data = await request.json()
        email = data.get('email')
        
        # Don't allow deleting the current admin
        if email == admin['email']:
            return JSONResponse(content={"error": "Cannot delete yourself"}, status_code=400)
        
        # Actually delete the user from database
        await database.execute(
            users.delete().where(users.c.email == email)
        )
        
        # Delete all sessions for this user
        await database.execute(
            user_sessions.delete().where(user_sessions.c.user_email == email)
        )
        
        # Log action
        client_ip = request.client.host if request.client else None
        await log_user_action(admin['email'], "delete_user", client_ip, details={"deleted_user": email})
        
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        print(f"Error deleting user: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/admin/company-mappings")
async def get_company_mappings(session_token: str = Cookie(None)):
    """Get all company email mappings (admin only)"""
    try:
        admin = await get_current_user(session_token)
        if not admin or admin['role'] != 'admin':
            return JSONResponse(content={"error": "Unauthorized"}, status_code=403)
        
        mappings = await database.fetch_all(company_email_mapping.select().order_by(company_email_mapping.c.company_name))
        
        result = []
        for m in mappings:
            result.append({
                'id': m['id'],
                'company_name': m['company_name'],
                'sender_email': m['sender_email'],
                'created_at': m['created_at'].isoformat() if m['created_at'] else None
            })
        
        return JSONResponse(content=result)
        
    except Exception as e:
        print(f"Error fetching mappings: {e}")
        return JSONResponse(content=[], status_code=500)

@app.post("/admin/add-company-mapping")
async def add_company_mapping(request: Request, session_token: str = Cookie(None)):
    """Add company email mapping (admin only)"""
    try:
        admin = await get_current_user(session_token)
        if not admin or admin['role'] != 'admin':
            return JSONResponse(content={"error": "Unauthorized"}, status_code=403)
        
        data = await request.json()
        company_name = data.get('company_name')
        sender_email = data.get('sender_email')
        
        if not company_name or not sender_email:
            return JSONResponse(content={"error": "Company name and sender email required"}, status_code=400)
        
        # Check if exists
        existing = await database.fetch_one(
            company_email_mapping.select().where(
                (company_email_mapping.c.company_name == company_name) |
                (company_email_mapping.c.sender_email == sender_email)
            )
        )
        
        if existing:
            return JSONResponse(content={"error": "Company or email already exists"}, status_code=400)
        
        # Add mapping
        await database.execute(
            company_email_mapping.insert().values(
                company_name=company_name,
                sender_email=sender_email
            )
        )
        
        # Log action
        client_ip = request.client.host if request.client else None
        await log_user_action(admin['email'], "add_company_mapping", client_ip, 
                            details={"company": company_name, "email": sender_email})
        
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        print(f"Error adding mapping: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/admin/delete-company-mapping")
async def delete_company_mapping(request: Request, session_token: str = Cookie(None)):
    """Delete company email mapping (admin only)"""
    try:
        admin = await get_current_user(session_token)
        if not admin or admin['role'] != 'admin':
            return JSONResponse(content={"error": "Unauthorized"}, status_code=403)
        
        data = await request.json()
        mapping_id = data.get('id')
        
        await database.execute(
            company_email_mapping.delete().where(company_email_mapping.c.id == mapping_id)
        )
        
        # Log action
        client_ip = request.client.host if request.client else None
        await log_user_action(admin['email'], "delete_company_mapping", client_ip, details={"id": mapping_id})
        
        return JSONResponse(content={"success": True})
        
    except Exception as e:
        print(f"Error deleting mapping: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/admin/audit-logs")
async def get_audit_logs(session_token: str = Cookie(None)):
    """Get audit logs (admin only)"""
    try:
        admin = await get_current_user(session_token)
        if not admin or admin['role'] != 'admin':
            return JSONResponse(content={"error": "Unauthorized"}, status_code=403)
        
        logs = await database.fetch_all(
            audit_log.select().order_by(audit_log.c.timestamp.desc()).limit(100)
        )
        
        result = []
        for log in logs:
            result.append({
                'user_email': log['user_email'],
                'action_type': log['action_type'],
                'bill_id': log['bill_id'],
                'company_name': log['company_name'],
                'timestamp': log['timestamp'].isoformat() if log['timestamp'] else None,
                'ip_address': log['ip_address']
            })
        
        return JSONResponse(content=result)
        
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return JSONResponse(content=[], status_code=500)

# --- Main Endpoints ---
@app.get("/", response_class=HTMLResponse)
async def root(request: Request, session_token: str = Cookie(None)):
    """Redirect to login or appropriate page based on auth status"""
    user = await get_current_user(session_token)
    
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Admin ONLY sees admin panel (NO access to bills dashboard)
    if user['role'] == 'admin':
        return RedirectResponse(url="/admin", status_code=303)
    else:
        # Regular users see bills dashboard
        return RedirectResponse(url="/dashboard", status_code=303)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, background_tasks: BackgroundTasks, session_token: str = Cookie(None)):
    """User dashboard - shows only their accessible company bills"""
    try:
        # Check authentication
        user = await get_current_user(session_token)
        if not user:
            return RedirectResponse(url="/login", status_code=303)
        
        # Update last activity
        await database.execute(
            user_sessions.update()
            .where(user_sessions.c.session_token == session_token)
            .values(last_activity=datetime.now(timezone.utc))
        )
        
        # Log page view
        client_ip = request.client.host if request.client else None
        await log_user_action(user['email'], "view_dashboard", client_ip)
        
        # Get user's accessible companies
        accessible_companies = user['accessible_companies'] if user['accessible_companies'] else []
        
        # Start background processing of new files (non-blocking)
        background_tasks.add_task(process_new_files_background)
        
        # Build dashboard list IMMEDIATELY from database (no waiting!)
        # For regular users: filter by accessible companies
        # For admin: this endpoint shouldn't be accessible (admins use /admin)
        
        if user['role'] == 'user' and accessible_companies:
            # Filter bills by company - get files from user's accessible company folders
            print(f"[DASHBOARD] User {user['email']} has access to companies: {accessible_companies}")
            
            # Get files from Google Drive folders for user's accessible companies
            service = get_drive_service()
            all_files = []
            
            for company_name in accessible_companies:
                print(f"[DASHBOARD] Getting files for company: {company_name}")
                
                # Get company folder
                company_query = f"'{SOURCE_FOLDER_ID}' in parents and name='{company_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
                company_results = service.files().list(q=company_query, fields="files(id)").execute()
                company_items = company_results.get('files', [])
                
                if company_items:
                    company_folder_id = company_items[0].get('id')
                    
                    # Get all PDFs in company folder and subfolders
                    pdf_query = f"'{company_folder_id}' in parents and mimeType='application/pdf' and trashed=false"
                    pdf_results = service.files().list(q=pdf_query, pageSize=100, fields="files(id,name,webViewLink,createdTime)").execute()
                    company_files = pdf_results.get('files', [])
                    all_files.extend(company_files)
                    print(f"[DASHBOARD] Found {len(company_files)} files in {company_name} folder")
            
            # Get file IDs from Drive
            drive_file_ids = [f['id'] for f in all_files]
            
            if drive_file_ids:
                # Filter database records by Drive file IDs
                bills_pending = await database.fetch_all(
                    bills.select().where(
                        (bills.c.status == 'Pending') & 
                        (bills.c.id.in_(drive_file_ids))
                    ).order_by(bills.c.upload_date.desc())
                )
                bpoil_pending = await database.fetch_all(
                    bpoil.select().where(
                        (bpoil.c.status == 'Pending') & 
                        (bpoil.c.drive_file_id.in_(drive_file_ids))
                    ).order_by(bpoil.c.upload_date.desc())
                )
            else:
                bills_pending = []
                bpoil_pending = []
                print(f"[DASHBOARD] No files found in accessible company folders")
        else:
            # Show all bills (for admin or users without company access)
            bills_pending = await database.fetch_all(
                bills.select().where(bills.c.status == 'Pending').order_by(bills.c.upload_date.desc())
            )
            bpoil_pending = await database.fetch_all(
                bpoil.select().where(bpoil.c.status == 'Pending').order_by(bpoil.c.upload_date.desc())
            )
        
        pending_bills = list(bills_pending) + list(bpoil_pending)

        bill_list = []
        seen_file_ids = set()  # Avoid duplicate entries from bpoil (multiple line items per file)
        
        for rec in pending_bills:
            d = dict(rec)
            
            # For bpoil table, only show each file once (skip duplicate line items)
            file_id = d.get('drive_file_id') or d.get('id')
            if file_id in seen_file_ids:
                continue
            seen_file_ids.add(file_id)
            
            # Use the ID that the frontend expects
            d['id'] = file_id
            
            # Convert ALL datetime and date objects to strings for JSON serialization
            for key, value in list(d.items()):
                if isinstance(value, datetime):
                    d[key] = value.isoformat()
                elif isinstance(value, date):
                    d[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    d[key] = float(value)
            
            # Use stored webViewLink from database (no need to fetch from Drive!)
            d['webViewLink'] = d.get('web_view_link', '')
            
            bill_list.append(d)

        # Get company names for display
        company_names = accessible_companies if accessible_companies else []
        
        return templates.TemplateResponse("home.html", {
            "request": request, 
            "bills": bill_list,
            "company_names": company_names,
            "user_email": user['email']
        })
    except Exception as e:
        print(f"Error in home endpoint: {e}")
        traceback.print_exc()
        return templates.TemplateResponse("home.html", {
            "request": request, 
            "bills": [],
            "company_names": [],
            "user_email": ""
        })

@app.get("/processing-status")
async def get_processing_status():
    """Get the current background processing status"""
    return JSONResponse(content=processing_status)

@app.get("/get-all-pending-bills")
async def get_all_pending_bills():
    """Get ALL pending bills for real-time dashboard updates"""
    try:
        # Get all pending bills from both tables
        bills_pending = await database.fetch_all(
            bills.select().where(bills.c.status == 'Pending').order_by(bills.c.upload_date.desc())
        )
        bpoil_pending = await database.fetch_all(
            bpoil.select().where(bpoil.c.status == 'Pending').order_by(bpoil.c.upload_date.desc())
        )
        
        pending_bills = list(bills_pending) + list(bpoil_pending)
        
        bill_list = []
        seen_file_ids = set()
        
        for rec in pending_bills:
            d = dict(rec)
            
            # For bpoil table, only show each file once
            file_id = d.get('drive_file_id') or d.get('id')
            if file_id in seen_file_ids:
                continue
            seen_file_ids.add(file_id)
            
            d['id'] = file_id
            
            # Convert datetime/date objects to strings
            for key, value in list(d.items()):
                if isinstance(value, datetime):
                    d[key] = value.isoformat()
                elif isinstance(value, date):
                    d[key] = value.isoformat()
                elif isinstance(value, Decimal):
                    d[key] = float(value)
            
            d['webViewLink'] = d.get('web_view_link', '')
            bill_list.append(d)
        
        return JSONResponse(content=bill_list)
        
    except Exception as e:
        print(f"Error in get-all-pending-bills: {e}")
        traceback.print_exc()
        return JSONResponse(content=[])

@app.post("/get-extracted-data")
async def get_extracted_data(request: Request, session_token: str = Cookie(None)):
    try:
        # Check authentication
        user = await get_current_user(session_token)
        if not user:
            return JSONResponse(content={"error": "Unauthorized - Please login"}, status_code=401)
        
        data = await request.json()
        file_id = data.get('file_id')

        # Check bills table first (for Allstar)
        query = bills.select().where(bills.c.id == file_id)
        bill = await database.fetch_one(query)
        
        # If not in bills table, check bpoil table (for BP Oil and Other)
        if not bill:
            bill = await database.fetch_one(bpoil.select().where(bpoil.c.drive_file_id == file_id))
        
        if not bill:
            return JSONResponse(content=[{"Error": "Bill not found"}])
        
        # Determine if this is from bpoil table (has auto-increment id) or bills table (has string id)
        bill_id = bill['id'] if 'id' in bill._mapping else None
        is_from_bpoil = isinstance(bill_id, int) if bill_id is not None else False
        
        # For BP Oil and Other suppliers (data is in bpoil table)
        if is_from_bpoil or (bill['supplier_name'] or '').lower() in ['bp oil', 'other']:
            # Get all rows for this file from bpoil table
            rows = await database.fetch_all(bpoil.select().where(bpoil.c.drive_file_id == file_id))
            if not rows:
                return JSONResponse(content=[{"Error": "No extracted data found"}])
            
            payload = []
            for r in rows:
                row_data = {
                    'Type': r['type'],
                    'A/C': r['a_c'],
                    'Date': r['date'].isoformat() if r['date'] else None,
                    'Ref': r['ref'],
                    'Ex.Ref': r['ex_ref'],
                    'N/C': r['n_c'],
                    'Dept': r['dept'],
                    'Details': r['details'],
                    'Net': float(r['net']) if r['net'] is not None else None,
                    'T/C': r['t_c'],
                    'VAT': float(r['vat']) if r['vat'] is not None else None,
                    'Bill Reference Number': r['bill_reference_number'] or '',
                }
                # Reorder keys to match desired column order
                key_order = ['Type', 'A/C', 'Date', 'Ref', 'Ex.Ref', 'N/C', 'Dept', 'Details', 'Net', 'T/C', 'VAT', 'Bill Reference Number']
                payload.append(reorder_dict_keys(row_data, key_order))
            return JSONResponse(content=payload)
        
        # For other suppliers, return extracted_data field with bill reference number
        if bill['extracted_data']:
            extracted_data = bill['extracted_data']
            # Add bill reference number to each row if it's a list
            if isinstance(extracted_data, list):
                # Compute Ref from filename once for fallback section
                try:
                    import re
                    filename_local = bill.get('filename') or ''
                    m_ref = re.search(r"(\d{6,})", filename_local)
                    ref_from_filename = m_ref.group(1) if m_ref else None
                except Exception:
                    ref_from_filename = None
                for item in extracted_data:
                    if isinstance(item, dict):
                        # Use bill_reference_number for bpoil table, invoice_reference for bills table
                        if 'bill_reference_number' in bill:
                            item['Bill Reference Number'] = bill['bill_reference_number'] or ''
                        else:
                            item['Bill Reference Number'] = bill['invoice_reference'] or ''
                        # Enforce Ref from filename only (6+ digits)
                        item['Ref'] = ref_from_filename
                
                # Reorder keys for other suppliers
                key_order = ['Type', 'A/C', 'Date', 'Ref', 'Ex.Ref', 'N/C', 'Dept', 'Details', 'Net', 'T/C', 'VAT', 'Bill Reference Number']
                reordered_data = []
                for item in extracted_data:
                    if isinstance(item, dict):
                        reordered_data.append(reorder_dict_keys(item, key_order))
                    else:
                        reordered_data.append(item)
                return JSONResponse(content=reordered_data)
        
        return JSONResponse(content=[{"Error": "No extracted data found"}])
        
    except Exception as e:
        print(f"Error getting extracted data: {e}")
        return JSONResponse(content=[{"Error": str(e)}])

@app.post("/get-objectified-data")
async def get_objectified_data(request: Request, session_token: str = Cookie(None)):
    """Get objectified (individual line items) data from bills."""
    try:
        # Check authentication
        user = await get_current_user(session_token)
        if not user:
            return JSONResponse(content={"error": "Unauthorized - Please login"}, status_code=401)
        
        data = await request.json()
        file_id = data.get('file_id')
        mode = data.get('mode', 'objectify')
        
        # Check both tables for the bill
        bill = await database.fetch_one(bills.select().where(bills.c.id == file_id))
        if not bill:
            # For bpoil table, need to get the first row with this drive_file_id
            bill = await database.fetch_one(bpoil.select().where(bpoil.c.drive_file_id == file_id))
        
        if not bill:
            return JSONResponse(content=[{"Error": "Bill not found"}])
        
        # Get the original file from Google Drive to reprocess
        service = get_drive_service()
        
        # Download the file
        try:
            req = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, req)
            done = False
            while not done:
                status, done = downloader.next_chunk()
            fh.seek(0)
        except Exception as e:
            print(f"Error downloading file for objectification: {e}")
            # Fall back to existing data if download fails
            if bill['extracted_data']:
                return JSONResponse(content=bill['extracted_data'])
            return JSONResponse(content=[{"Error": "Could not download file for objectification"}])
        
        # Process with objectify mode based on supplier
        supplier_lower = (bill['supplier_name'] or '').lower()
        
        if supplier_lower == 'bp oil':
            # For BP Oil, return existing line items from bpoil table
            # BP Oil bills already have multiple line items
            rows = await database.fetch_all(bpoil.select().where(bpoil.c.drive_file_id == file_id))
            if rows:
                payload = []
                for r in rows:
                    payload.append({
                        'Type': r['type'],
                        'A/C': r['a_c'],
                        'Date': r['date'].isoformat() if r['date'] else None,
                        'Ref': r['ref'],
                        'Ex.Ref': r['ex_ref'],
                        'N/C': r['n_c'],
                        'Dept': r['dept'],
                        'Details': r['details'],
                        'Net': float(r['net']) if r['net'] is not None else None,
                        'T/C': r['t_c'],
                        'VAT': float(r['vat']) if r['vat'] is not None else None,
                        'Bill Reference Number': r['bill_reference_number'] or '',
                    })
                return JSONResponse(content=payload)
        
        elif supplier_lower == 'allstar':
            # For Allstar, would need to update allstar_processor.py
            # For now, return existing data with bill reference number
            if bill['extracted_data']:
                extracted_data = bill['extracted_data']
                # Add bill reference number to each row if it's a list
                if isinstance(extracted_data, list):
                    # Force Ref to be derived strictly from filename (6+ digits)
                    try:
                        import re
                        filename_local = bill.get('filename') or ''
                        m_ref = re.search(r"(\d{6,})", filename_local)
                        ref_from_filename = m_ref.group(1) if m_ref else None
                    except Exception:
                        ref_from_filename = None
                    for item in extracted_data:
                        if isinstance(item, dict):
                            # Use bill_reference_number for bpoil table, invoice_reference for bills table
                            if 'bill_reference_number' in bill:
                                item['Bill Reference Number'] = bill['bill_reference_number'] or ''
                            else:
                                item['Bill Reference Number'] = bill['invoice_reference'] or ''
                            # Enforce Ref from filename only (never invoice number)
                            item['Ref'] = ref_from_filename
                return JSONResponse(content=extracted_data)
        
        else:
            # For Other suppliers, use the objectified processor
            from processors import other_processor
            
            # Get filename and upload date
            filename = bill['filename']
            upload_date = bill['upload_date'].isoformat() if bill['upload_date'] else None
            
            # Process with objectify mode
            try:
                extraction_result = other_processor.process_bill_objectified(
                    fh, filename, upload_date
                )
                line_items = extraction_result.get('line_items', [])
                
                # Add bill reference number to each line item
                for item in line_items:
                    if isinstance(item, dict):
                        # Use bill_reference_number for bpoil table, invoice_reference for bills table
                        if 'bill_reference_number' in bill:
                            item['Bill Reference Number'] = bill['bill_reference_number'] or ''
                        else:
                            item['Bill Reference Number'] = bill['invoice_reference'] or ''
                        # Enforce Ref from filename only (6+ digits)
                        try:
                            import re
                            m_ref = re.search(r"(\d{6,})", filename or '')
                            item['Ref'] = m_ref.group(1) if m_ref else None
                        except Exception:
                            item['Ref'] = None
                
                # Reorder keys for objectified data
                key_order = ['Type', 'A/C', 'Date', 'Ref', 'Ex.Ref', 'N/C', 'Dept', 'Details', 'Net', 'T/C', 'VAT', 'Bill Reference Number']
                reordered_line_items = []
                for item in line_items:
                    if isinstance(item, dict):
                        reordered_line_items.append(reorder_dict_keys(item, key_order))
                    else:
                        reordered_line_items.append(item)
                return JSONResponse(content=reordered_line_items)
            except Exception as e:
                print(f"Error in objectified extraction: {e}")
                # Fall back to existing data
                if bill['extracted_data']:
                    # Reorder keys for fallback data
                    key_order = ['Type', 'A/C', 'Date', 'Ref', 'Ex.Ref', 'N/C', 'Dept', 'Details', 'Net', 'T/C', 'VAT', 'Bill Reference Number']
                    fallback_data = bill['extracted_data']
                    if isinstance(fallback_data, list):
                        reordered_fallback = []
                        for item in fallback_data:
                            if isinstance(item, dict):
                                reordered_fallback.append(reorder_dict_keys(item, key_order))
                            else:
                                reordered_fallback.append(item)
                        return JSONResponse(content=reordered_fallback)
                    return JSONResponse(content=fallback_data)
                return JSONResponse(content=[{"Error": f"Objectification failed: {e}"}])
        
        # Default fallback
        if bill['extracted_data']:
            extracted_data = bill['extracted_data']
            # Add bill reference number to each row if it's a list
            if isinstance(extracted_data, list):
                # Compute Ref from filename once
                try:
                    import re
                    filename_local = bill.get('filename') or ''
                    m_ref = re.search(r"(\d{6,})", filename_local)
                    ref_from_filename = m_ref.group(1) if m_ref else None
                except Exception:
                    ref_from_filename = None
                for item in extracted_data:
                    if isinstance(item, dict):
                        # Use bill_reference_number for bpoil table, invoice_reference for bills table
                        if 'bill_reference_number' in bill:
                            item['Bill Reference Number'] = bill['bill_reference_number'] or ''
                        else:
                            item['Bill Reference Number'] = bill['invoice_reference'] or ''
                
                # Reorder keys for default fallback
                key_order = ['Type', 'A/C', 'Date', 'Ref', 'Ex.Ref', 'N/C', 'Dept', 'Details', 'Net', 'T/C', 'VAT', 'Bill Reference Number']
                reordered_fallback = []
                for item in extracted_data:
                    if isinstance(item, dict):
                        reordered_fallback.append(reorder_dict_keys(item, key_order))
                    else:
                        reordered_fallback.append(item)
                return JSONResponse(content=reordered_fallback)
        return JSONResponse(content=[{"Error": "No objectified data available"}])
        
    except Exception as e:
        print(f"Error getting objectified data: {e}")
        return JSONResponse(content=[{"Error": str(e)}])

@app.post("/approve")
async def approve_bill(request: Request, session_token: str = Cookie(None)):
    try:
        # Check authentication
        user = await get_current_user(session_token)
        if not user:
            return JSONResponse(content={"error": "Unauthorized - Please login"}, status_code=401)
        
        data = await request.json()
        file_id = data.get('file_id')
        corrected_data = data.get('corrected_data')
        client_ip = request.client.host if request.client else None
        
        print(f"\n[APPROVE] Starting approval for file_id: {file_id} by user: {user['email']}")
        
        # Update database - check both tables
        # First check if bill exists in bills table (Allstar)
        bill_exists_in_bills = await database.fetch_one(bills.select().where(bills.c.id == file_id))
        
        if bill_exists_in_bills:
            # Update in bills table
            await database.execute(
            bills.update().where(bills.c.id == file_id).values(
                status='Approved',
                extracted_data=corrected_data
            )
        )
            print("[APPROVE] ✓ Updated bills table (Allstar)")
        else:
            # Update in bpoil table (BP Oil and Other)
            # For bpoil, update ALL rows with this drive_file_id
            await database.execute(
                bpoil.update().where(bpoil.c.drive_file_id == file_id).values(
                    status='Approved',
                    extracted_data=corrected_data
                )
            )
            print("[APPROVE] ✓ Updated bpoil table (BP Oil/Other)")
        
        print("[APPROVE] ✓ Database updated to Approved status")
        
        # Get bill details from both tables
        bill = await database.fetch_one(bills.select().where(bills.c.id == file_id))
        if not bill:
            # For bpoil, get the first row with this drive_file_id
            bill = await database.fetch_one(bpoil.select().where(bpoil.c.drive_file_id == file_id))
        
        if not bill:
            return JSONResponse(content={"error": "Bill not found"}, status_code=404)
        
        print(f"[APPROVE] Bill found: {bill.filename} | ID: {bill.id} | Drive ID: {bill.drive_file_id}")
        print(f"[APPROVE] Bill mapping keys: {list(bill._mapping.keys())}")
        
        # Move file in Google Drive
        try:
            print(f"[APPROVE] Getting Google Drive service...")
            service = get_drive_service()
            print(f"[APPROVE] Drive service obtained successfully")
            
            # Test Drive service by listing a few files
            try:
                test_query = f"'{SOURCE_FOLDER_ID}' in parents and mimeType='application/pdf' and trashed=false"
                test_results = service.files().list(q=test_query, pageSize=1, fields="files(id,name)").execute()
                print(f"[APPROVE] Drive service test successful - found {len(test_results.get('files', []))} files")
            except Exception as test_error:
                print(f"[APPROVE] Drive service test failed: {test_error}")
                return JSONResponse(content={"error": f"Google Drive service error: {str(test_error)}"}, status_code=500)
            
            supplier_name = bill['supplier_name'] or 'Misc'
            is_bp_oil = supplier_name.lower() == 'bp oil'
            is_allstar = supplier_name.lower() == 'allstar'
            is_other = not is_bp_oil and not is_allstar
            
            print(f"[APPROVE] Processing {supplier_name} bill")
            
            # Step 1: Determine company name (default to PRL for now)
            company_name = "PRL"  # Default to PRL since we only have PRL configured
            print(f"[APPROVE] Using company: {company_name}")
            
            # Step 2: Create/find company folder in Approved Bills
            company_query = f"'{DESTINATION_PARENT_FOLDER_ID}' in parents and name='{company_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            company_results = service.files().list(q=company_query, fields="files(id)").execute()
            company_items = company_results.get('files', [])
            
            if not company_items:
                # Create company folder
                company_metadata = {
                    'name': company_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [DESTINATION_PARENT_FOLDER_ID]
                }
                company_folder = service.files().create(body=company_metadata, fields='id').execute()
                company_folder_id = company_folder.get('id')
                print(f"[APPROVE] Created company folder: {company_name}")
            else:
                company_folder_id = company_items[0].get('id')
                print(f"[APPROVE] Found company folder: {company_name}")
            
            # Step 3: Create/find month folder (YYYY-MM format from invoice date)
            month_name = datetime.now().strftime('%Y-%m')  # Default to current month
            inv_dt = bill['invoice_date'] if 'invoice_date' in bill._mapping else None
            if inv_dt:
                # Handle both date objects and ISO strings
                if isinstance(inv_dt, str):
                    try:
                        from datetime import datetime as dt
                        inv_dt = dt.fromisoformat(inv_dt).date()
                    except:
                        inv_dt = None
                
            if inv_dt:
                month_name = inv_dt.strftime('%Y-%m')
                print(f"[APPROVE] Using invoice date for month: {month_name}")
            
            month_query = f"'{company_folder_id}' in parents and name='{month_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
            month_results = service.files().list(q=month_query, fields="files(id)").execute()
            month_items = month_results.get('files', [])
            
            if not month_items:
                # Create month folder
                month_metadata = {
                    'name': month_name,
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': [company_folder_id]
                }
                month_folder = service.files().create(body=month_metadata, fields='id').execute()
                final_parent_id = month_folder.get('id')
                print(f"[APPROVE] Created month folder: {month_name}")
            else:
                final_parent_id = month_items[0].get('id')
                print(f"[APPROVE] Found month folder: {month_name}")
            
            # Step 4: Move file to final destination
            # Get the actual drive file ID (differs between bills and bpoil tables)
            actual_drive_file_id = bill.drive_file_id if hasattr(bill, 'drive_file_id') else bill.id
            print(f"[APPROVE] Using drive file ID: {actual_drive_file_id}")
            
            try:
                print(f"[APPROVE] Attempting to get file info for ID: {actual_drive_file_id}")
                file_info = service.files().get(fileId=actual_drive_file_id, fields='parents,name').execute()
                prev_parents_list = file_info.get('parents') or []
                previous_parents = ",".join(prev_parents_list)
                print(f"[APPROVE] File found: {file_info.get('name')} in parents: {previous_parents}")
            except Exception as file_error:
                print(f"[APPROVE] ERROR getting file info: {type(file_error).__name__}: {file_error}")
                print(f"[APPROVE] File ID that failed: {actual_drive_file_id}")
                print(f"[APPROVE] Bill data: {dict(bill._mapping)}")
                return JSONResponse(content={"error": f"File not found in Drive: {type(file_error).__name__}: {str(file_error)}"}, status_code=404)
            
            # Move the file
            try:
                move_result = service.files().update(
                    fileId=actual_drive_file_id,
                    addParents=final_parent_id,
                    removeParents=previous_parents,
                    fields='id, parents'
                ).execute()
                print(f"[APPROVE] File moved successfully: {move_result.get('id')}")
            except Exception as move_error:
                print(f"[APPROVE] Error moving file: {move_error}")
                return JSONResponse(content={"error": f"Failed to move file: {str(move_error)}"}, status_code=500)
            
            print(f"[APPROVE] ✓ Moved file to: Approved/{company_name}/{month_name}/")
            
            # Generate drive address for Ref column
            drive_address = f"Approved/{company_name}/{month_name}/{bill.filename}"
            print(f"[APPROVE] Drive address: {drive_address}")
            
            # Update database with drive address
            if bill_exists_in_bills:
                # Update in bills table
                await database.execute(
                    bills.update().where(bills.c.id == file_id).values(
                        status='Approved',
                        extracted_data=corrected_data,
                        ref=drive_address  # Update Ref column with drive address
                    )
                )
                print("[APPROVE] ✓ Updated bills table (Allstar)")
            else:
                # Update in bpoil table (BP Oil and Other)
                await database.execute(
                    bpoil.update().where(bpoil.c.drive_file_id == file_id).values(
                        status='Approved',
                        extracted_data=corrected_data,
                        ref=drive_address  # Update Ref column with drive address
                    )
                )
                print("[APPROVE] ✓ Updated bpoil table (BP Oil/Other)")
            
            # Log the approval action
            await log_user_action(user['email'], "approve_bill", client_ip, 
                                details={"bill_id": file_id, "company": company_name, "month": month_name})
            
            return JSONResponse(content={"success": True, "message": f"Bill approved and moved to Approved/{company_name}/{month_name}/"})
            
        except Exception as e:
            print(f"[APPROVE] Drive operation error: {e}")
            traceback.print_exc()
            return JSONResponse(content={"error": f"Drive operation failed: {str(e)}"}, status_code=500)
        
    except Exception as e:
        print(f"[APPROVE] Error: {e}")
        traceback.print_exc()
        return JSONResponse(content={"error": f"Approval failed: {str(e)}"}, status_code=500)

# --- Rescan endpoint ---
@app.get("/rescan")
async def rescan_all():
    try:
        service = get_drive_service()
        # list all PDFs under SOURCE_FOLDER_ID (top-level only for simplicity)
        query = f"'{SOURCE_FOLDER_ID}' in parents and mimeType='application/pdf' and trashed=false"
        results = service.files().list(q=query, pageSize=200, fields="files(id, name, webViewLink, createdTime)").execute()
        files = results.get('files', [])
        refreshed = 0
        for f in files:
            try:
                # Check if file already exists in database
                existing_bill = await database.fetch_one(
                    bills.select().where(bills.c.id == f['id'])
                )
                existing_bpoil = await database.fetch_one(
                    bpoil.select().where(bpoil.c.drive_file_id == f['id'])
                )
                
                if existing_bill or existing_bpoil:
                    continue  # Skip if already processed
                
                # Download and process the file
                request = service.files().get_media(fileId=f['id'])
                file_data = io.BytesIO()
                downloader = MediaIoBaseDownload(file_data, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                file_data.seek(0)
                
                # Process the file
                extraction_result = route_and_process_bill(file_data, f['name'], f['createdTime'])
                
                if 'error' not in extraction_result:
                    # Save to database
                    if extraction_result.get('supplier_name', '').lower() == 'allstar':
                        await database.execute(
                            bills.insert().values(
                            id=f['id'],
                            drive_file_id=f['id'],
                                invoice_reference=extraction_result.get('invoice_reference'),
                                filename=f['name'],
                                supplier_name=extraction_result.get('supplier_name'),
                                upload_date=datetime.now(timezone.utc),
                                invoice_date=extraction_result.get('invoice_date'),
                                gross_amount=extraction_result.get('gross_amount'),
                            status='Pending',
                                extracted_data=extraction_result.get('extracted_data'),
                                web_view_link=f['webViewLink']
                            )
                        )
                else:
                        await database.execute(
                            bpoil.insert().values(
                                drive_file_id=f['id'],
                                invoice_reference=extraction_result.get('invoice_reference'),
                                filename=f['name'],
                                supplier_name=extraction_result.get('supplier_name'),
                                upload_date=datetime.now(timezone.utc),
                                invoice_date=extraction_result.get('invoice_date'),
                                gross_amount=extraction_result.get('gross_amount'),
                                status='Pending',
                                extracted_data=extraction_result.get('extracted_data'),
                                web_view_link=f['webViewLink']
                            )
                        )
                refreshed += 1
            except Exception as e:
                print(f"[Rescan] Skip {f['name']}: {e}")
        return JSONResponse(content={"success": True, "refreshed": refreshed})
    except Exception as e:
        print(f"[Rescan] Error: {e}")
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

def create_company_month_folder_for_upload(service, company_name, invoice_date):
    """Create Pending/Company/Month folder structure for uploads"""
    try:
        # Get or create company folder in Pending Bills
        company_query = f"'{SOURCE_FOLDER_ID}' in parents and name='{company_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        company_results = service.files().list(q=company_query, fields="files(id)").execute()
        company_items = company_results.get('files', [])
        
        if not company_items:
            # Create company folder
            company_metadata = {
                'name': company_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [SOURCE_FOLDER_ID]
            }
            company_folder = service.files().create(body=company_metadata, fields='id').execute()
            company_folder_id = company_folder.get('id')
            print(f"[UPLOAD] Created company folder: {company_name}")
        else:
            company_folder_id = company_items[0].get('id')
            print(f"[UPLOAD] Found company folder: {company_name}")
        
        # Get or create month folder (YYYY-MM format)
        if invoice_date:
            if isinstance(invoice_date, str):
                try:
                    from datetime import datetime as dt
                    invoice_date = dt.fromisoformat(invoice_date).date()
                except:
                    invoice_date = None
            
            if invoice_date:
                month_name = invoice_date.strftime('%Y-%m')
            else:
                month_name = datetime.now().strftime('%Y-%m')
        else:
            month_name = datetime.now().strftime('%Y-%m')
        
        month_query = f"'{company_folder_id}' in parents and name='{month_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        month_results = service.files().list(q=month_query, fields="files(id)").execute()
        month_items = month_results.get('files', [])
        
        if not month_items:
            # Create month folder
            month_metadata = {
                'name': month_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [company_folder_id]
            }
            month_folder = service.files().create(body=month_metadata, fields='id').execute()
            month_folder_id = month_folder.get('id')
            print(f"[UPLOAD] Created month folder: {month_name}")
        else:
            month_folder_id = month_items[0].get('id')
            print(f"[UPLOAD] Found month folder: {month_name}")
        
        return month_folder_id
        
    except Exception as e:
        print(f"[UPLOAD] Error creating company/month folder: {e}")
        return SOURCE_FOLDER_ID  # Fallback to main folder

# --- Upload Endpoint: PDF + optional supplier, upload to Drive, extract, save to DB ---
@app.post("/upload-bill")
async def upload_bill(request: Request, file: UploadFile = File(...), supplier: str | None = Form(None), session_token: str = Cookie(None)):
    try:
        print(f"[UPLOAD] ===== UPLOAD ENDPOINT CALLED =====")
        print(f"[UPLOAD] File: {file.filename}")
        print(f"[UPLOAD] Session token: {session_token[:20] if session_token else 'None'}...")
        
        # Authentication check
        user = await get_current_user(session_token)
        if not user:
            print(f"[UPLOAD] ERROR: Authentication failed")
            return JSONResponse(content={"error": "Authentication required"}, status_code=401)
        
        print(f"[UPLOAD] User authenticated: {user['email']}")
        
        # Get user's accessible companies
        accessible_companies = user.get('accessible_companies', [])
        print(f"[UPLOAD] User {user['email']} accessible companies: {accessible_companies}")
        
        if not accessible_companies:
            print(f"[UPLOAD] ERROR: No company access granted for user {user['email']}")
            return JSONResponse(content={"error": "No company access granted"}, status_code=403)
        
        # For now, use the first company (PRL) - later can be selected by user
        company_name = accessible_companies[0] if accessible_companies else "PRL"
        print(f"[UPLOAD] User {user['email']} uploading to company: {company_name}")
        
        # Get Google Drive service
        print(f"[UPLOAD] Getting Google Drive service...")
        try:
            service = get_drive_service()
            print(f"[UPLOAD] Drive service obtained successfully")
        except Exception as service_error:
            print(f"[UPLOAD] ERROR getting Drive service: {service_error}")
            return JSONResponse(content={"error": f"Google Drive service error: {str(service_error)}"}, status_code=500)
        
        file_content = await file.read()
        print(f"[UPLOAD] File content read: {len(file_content)} bytes")
        
        # Create company/month folder structure for upload
        print(f"[UPLOAD] Creating company/month folder for {company_name}...")
        try:
            target_folder_id = create_company_month_folder_for_upload(service, company_name, None)
            print(f"[UPLOAD] Target folder ID: {target_folder_id}")
        except Exception as folder_error:
            print(f"[UPLOAD] ERROR creating folder: {folder_error}")
            return JSONResponse(content={"error": f"Folder creation failed: {str(folder_error)}"}, status_code=500)
        
        print(f"[UPLOAD] Preparing file upload...")
        try:
            media = MediaIoBaseUpload(
                io.BytesIO(file_content),
                mimetype='application/pdf',
                resumable=True
            )
            print(f"[UPLOAD] Media object created successfully")
            
            file_metadata = {
            'name': file.filename,
                'parents': [target_folder_id]
            }
            print(f"[UPLOAD] File metadata: {file_metadata}")
            
            print(f"[UPLOAD] Uploading file to Google Drive...")
            uploaded_file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, name, webViewLink'
            ).execute()
            print(f"[UPLOAD] File uploaded successfully: {uploaded_file.get('id')}")
        except Exception as upload_error:
            print(f"[UPLOAD] ERROR uploading file: {upload_error}")
            return JSONResponse(content={"error": f"File upload failed: {str(upload_error)}"}, status_code=500)
        
        # Process the uploaded file
        print(f"[UPLOAD] Processing file for extraction...")
        try:
            file_data = io.BytesIO(file_content)
            extraction_result = route_and_process_bill(file_data, file.filename, datetime.now(timezone.utc))
            print(f"[UPLOAD] Extraction result: {extraction_result.get('supplier_name', 'Unknown')} - {extraction_result.get('invoice_reference', 'No ref')}")
        except Exception as process_error:
            print(f"[UPLOAD] ERROR processing file: {process_error}")
            return JSONResponse(content={"error": f"File processing failed: {str(process_error)}"}, status_code=500)
        
        if 'error' in extraction_result:
            print(f"[UPLOAD] ERROR in extraction: {extraction_result['error']}")
            return JSONResponse(content={"error": extraction_result['error']}, status_code=400)
        
        # Save to database
        print(f"[UPLOAD] Saving to database...")
        try:
            if extraction_result.get('supplier_name', '').lower() == 'allstar':
                print(f"[UPLOAD] Saving to bills table (Allstar)")
                await database.execute(
                    bills.insert().values(
                        id=uploaded_file['id'],
                        drive_file_id=uploaded_file['id'],
                        invoice_reference=extraction_result.get('invoice_reference'),
                        filename=file.filename,
                        supplier_name=extraction_result.get('supplier_name'),
                        upload_date=datetime.now(timezone.utc),
                        invoice_date=extraction_result.get('invoice_date'),
                        gross_amount=extraction_result.get('gross_amount'),
                        status='Pending',
                        extracted_data=extraction_result.get('extracted_data'),
                        web_view_link=uploaded_file['webViewLink']
                    )
                )
            else:
                print(f"[UPLOAD] Saving to bpoil table (BP Oil/Other)")
                await database.execute(
                    bpoil.insert().values(
                        drive_file_id=uploaded_file['id'],
                        invoice_reference=extraction_result.get('invoice_reference'),
                        filename=file.filename,
                        supplier_name=extraction_result.get('supplier_name'),
                        upload_date=datetime.now(timezone.utc),
                        invoice_date=extraction_result.get('invoice_date'),
                        gross_amount=extraction_result.get('gross_amount'),
                        status='Pending',
                        extracted_data=extraction_result.get('extracted_data'),
                        web_view_link=uploaded_file['webViewLink']
                    )
                )
            print(f"[UPLOAD] Database save successful")
        except Exception as db_error:
            print(f"[UPLOAD] ERROR saving to database: {db_error}")
            return JSONResponse(content={"error": f"Database save failed: {str(db_error)}"}, status_code=500)
        
        return JSONResponse(content={"success": True, "message": f"File uploaded and processed successfully to {company_name} folder"})

    except Exception as e:
        print(f"Upload error: {e}")
        traceback.print_exc()
        return JSONResponse(content={"error": str(e)}, status_code=500)

# --- Test endpoint to verify server is working ---
@app.get("/test-upload")
async def test_upload():
    return JSONResponse(content={"message": "Upload endpoint is working", "status": "ok"})

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
