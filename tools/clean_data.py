import os
import sys
import argparse
from contextlib import contextmanager

from sqlalchemy import create_engine, text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Clean runtime data before going live: clears bills, bpoil, sessions (optional audit_log)."
    )
    parser.add_argument(
        "--database-url",
        dest="database_url",
        default=os.getenv("DATABASE_URL"),
        help="Database URL. Defaults to DATABASE_URL env var.",
    )
    parser.add_argument(
        "--include-audit",
        action="store_true",
        help="Also clear audit_log table data.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what will be executed without performing changes.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Run non-interactively without confirmation prompt.",
    )
    return parser.parse_args()


@contextmanager
def engine_ctx(database_url: str):
    engine = create_engine(database_url, future=True)
    try:
        yield engine
    finally:
        engine.dispose()


def confirm_or_exit(include_audit: bool, non_interactive_yes: bool) -> None:
    print("This will DELETE DATA from the following tables (schema preserved):")
    print(" - bills")
    print(" - bpoil")
    print(" - user_sessions")
    if include_audit:
        print(" - audit_log")

    if non_interactive_yes:
        return

    answer = input("Type 'DELETE' to proceed: ").strip()
    if answer != "DELETE":
        print("Aborted.")
        sys.exit(1)


def build_sql(include_audit: bool) -> list[str]:
    # Use TRUNCATE to be fast and reset sequences; CASCADE to satisfy FKs to these tables
    stmts: list[str] = [
        "TRUNCATE TABLE bills RESTART IDENTITY CASCADE;",
        "TRUNCATE TABLE bpoil RESTART IDENTITY CASCADE;",
        "TRUNCATE TABLE user_sessions RESTART IDENTITY CASCADE;",
    ]
    if include_audit:
        stmts.append("TRUNCATE TABLE audit_log RESTART IDENTITY CASCADE;")
    return stmts


def main() -> None:
    args = parse_args()

    if not args.database_url:
        print("ERROR: DATABASE_URL not provided. Set env var or pass --database-url.")
        sys.exit(2)

    confirm_or_exit(include_audit=args.include_audit, non_interactive_yes=args.yes)

    stmts = build_sql(include_audit=args.include_audit)

    if args.dry_run:
        print("-- DRY RUN -- The following statements would be executed:")
        for s in stmts:
            print(s)
        return

    with engine_ctx(args.database_url) as engine:
        with engine.begin() as conn:
            for s in stmts:
                conn.execute(text(s))

    print("✅ Data cleared successfully.")


if __name__ == "__main__":
    main()


