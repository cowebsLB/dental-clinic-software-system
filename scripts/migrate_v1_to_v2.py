"""Migrate v1 SQLite data into v2 backend schema.

Usage:
  python scripts/migrate_v1_to_v2.py --source ./data/local_cache.db --target ./data/v2.db --report ./docs/migration-report.json
"""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from datetime import datetime, UTC

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src_v2.infrastructure.sqlite_connection import connect
from src_v2.infrastructure.sqlite_schema import initialize_schema


def _read_count(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()
    return int(row[0]) if row else 0


def migrate(source: str, target: str) -> dict:
    source_conn = sqlite3.connect(source)
    source_conn.row_factory = sqlite3.Row
    target_conn = connect(target)
    initialize_schema(target_conn)

    report = {
        "started_at": datetime.now(UTC).isoformat(),
        "source": source,
        "target": target,
        "tables": {},
        "errors": [],
    }

    mappings = [
        ("clients", "patients", ("id", "first_name", "last_name", "phone", "email", "created_at", "updated_at")),
        ("reservations", "appointments", ("id", "client_id", "doctor_id", "start_time_utc", "status", "notes", "created_at", "updated_at")),
        ("invoices", "invoices", ("id", "client_id", "reservation_id", "total", "status", "created_at", "updated_at")),
    ]

    for source_table, target_table, fields in mappings:
        try:
            rows = source_conn.execute(f"SELECT * FROM {source_table}").fetchall()
            moved = 0
            for row in rows:
                if target_table == "patients":
                    target_conn.execute(
                        "INSERT OR IGNORE INTO patients (id, first_name, last_name, phone, email, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        tuple(row[f] or "" for f in fields),
                    )
                elif target_table == "appointments":
                    target_conn.execute(
                        """
                        INSERT OR IGNORE INTO appointments (id, patient_id, doctor_id, appointment_at, status, notes, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        tuple(row[f] or "" for f in fields),
                    )
                elif target_table == "invoices":
                    target_conn.execute(
                        """
                        INSERT OR IGNORE INTO invoices (id, patient_id, appointment_id, amount, status, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        tuple(row[f] or "" for f in fields),
                    )
                moved += 1
            target_conn.commit()
            report["tables"][source_table] = {"source_rows": len(rows), "migrated_rows": moved}
        except Exception as exc:
            report["errors"].append(f"{source_table}: {exc}")

    report["target_counts"] = {
        "patients": _read_count(target_conn, "patients"),
        "appointments": _read_count(target_conn, "appointments"),
        "invoices": _read_count(target_conn, "invoices"),
    }
    report["completed_at"] = datetime.now(UTC).isoformat()
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--target", required=True)
    parser.add_argument("--report", required=True)
    args = parser.parse_args()

    report = migrate(args.source, args.target)
    with open(args.report, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
