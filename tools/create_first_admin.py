"""
Create the first admin account
Email: ayush23854@gmail.com
Password: ayush23854@
"""

import asyncio
import databases
import hashlib

DATABASE_URL = "postgresql://bill_user:ayush23854@localhost/bill_processor_db"

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

async def create_first_admin():
    """Create the first admin account"""
    database = databases.Database(DATABASE_URL)
    
    try:
        await database.connect()
        print("Connected to database")
        
        admin_email = "ayush23854@gmail.com"
        admin_password = "ayush23854@"
        
        # Check if admin already exists
        existing = await database.fetch_one(
            "SELECT * FROM users WHERE email = :email",
            {"email": admin_email}
        )
        
        if existing:
            print(f"✓ Admin account already exists: {admin_email}")
        else:
            # Create admin account
            password_hash = hash_password(admin_password)
            
            await database.execute(
                """INSERT INTO users (email, password_hash, role, accessible_companies, is_active, created_by)
                   VALUES (:email, :password_hash, :role, :accessible_companies, :is_active, :created_by)""",
                {
                    "email": admin_email,
                    "password_hash": password_hash,
                    "role": "admin",
                    "accessible_companies": None,  # Admin sees everything
                    "is_active": True,
                    "created_by": "system"
                }
            )
            
            print(f"\n✅ Successfully created admin account!")
            print(f"   Email: {admin_email}")
            print(f"   Password: {admin_password}")
            print(f"   Role: admin")
        
        await database.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_first_admin())

