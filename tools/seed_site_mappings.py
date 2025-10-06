import csv
from pathlib import Path
from sqlalchemy import create_engine, text


DATABASE_URL = "postgresql://bill_user:ayush23854@localhost/bill_processor_db"
CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "site_mappings.csv"


def main() -> None:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    if not CSV_PATH.exists():
        raise SystemExit(f"CSV not found: {CSV_PATH}")

    with engine.begin() as conn, CSV_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        if not rows:
            print("No rows found in CSV.")
            return

        stmt = text(
            """
            INSERT INTO site_mappings (site_name, dept, ac_code, short_code, company, post_code)
            VALUES (:site_name, :dept, :ac_code, :short_code, :company, :post_code)
            ON CONFLICT (site_name) DO UPDATE SET
                dept = EXCLUDED.dept,
                ac_code = EXCLUDED.ac_code,
                short_code = EXCLUDED.short_code,
                company = EXCLUDED.company,
                post_code = EXCLUDED.post_code
            """
        )

        for r in rows:
            payload = {
                "site_name": (r.get("site_name") or "").strip(),
                "dept": (r.get("dept") or "").strip() or None,
                "ac_code": (r.get("ac_code") or "").strip() or None,
                "short_code": (r.get("short_code") or "").strip() or None,
                "company": (r.get("company") or "").strip() or None,
                "post_code": (r.get("post_code") or "").strip() or None,
            }
            if not payload["site_name"]:
                continue
            conn.execute(stmt, payload)

    print(f"Seeded site_mappings from {CSV_PATH}")


if __name__ == "__main__":
    main()


