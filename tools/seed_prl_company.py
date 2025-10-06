"""
Seed the company_email_mapping table with PRL company
Admin can add more companies later via admin panel
"""

import asyncio
import databases

DATABASE_URL = "postgresql://bill_user:ayush23854@localhost/bill_processor_db"

async def seed_prl_company():
    """Seed PRL company mapping"""
    database = databases.Database(DATABASE_URL)
    
    try:
        await database.connect()
        print("Connected to database")
        
        # Check if PRL already exists
        existing = await database.fetch_one(
            "SELECT * FROM company_email_mapping WHERE company_name = 'PRL'"
        )
        
        if existing:
            print("✓ PRL company mapping already exists")
        else:
            # Add PRL company
            # You can update the sender email later via admin panel
            await database.execute(
                """INSERT INTO company_email_mapping (company_name, sender_email)
                   VALUES (:company_name, :sender_email)""",
                {
                    "company_name": "PRL",
                    "sender_email": "prl@example.com"  # Placeholder - update via admin panel
                }
            )
            
            print("\n✅ Successfully created PRL company mapping!")
            print("   Company: PRL")
            print("   Sender Email: prl@example.com (placeholder)")
            print("\n   ⚠️  Update the sender email via Admin Panel to match actual PRL sender email")
        
        await database.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(seed_prl_company())

