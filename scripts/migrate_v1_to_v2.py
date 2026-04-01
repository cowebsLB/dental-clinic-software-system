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


def _value(row: sqlite3.Row, key: str, default=""):
    return row[key] if key in row.keys() and row[key] is not None else default


def _build_patient_params(row: sqlite3.Row) -> tuple:
    return (
        _value(row, "id"),
        _value(row, "first_name"),
        _value(row, "last_name"),
        _value(row, "phone"),
        _value(row, "email"),
        _value(row, "created_at"),
        _value(row, "updated_at"),
    )


def _build_appointment_params(row: sqlite3.Row) -> tuple:
    return (
        _value(row, "id"),
        _value(row, "client_id"),  # v1 -> v2 patient_id
        _value(row, "doctor_id"),
        _value(row, "start_time_utc"),  # v1 -> v2 appointment_at
        _value(row, "status"),
        _value(row, "notes"),
        _value(row, "created_at"),
        _value(row, "updated_at"),
    )


def _build_invoice_params(row: sqlite3.Row) -> tuple:
    return (
        _value(row, "id"),
        _value(row, "client_id"),  # v1 -> v2 patient_id
        _value(row, "reservation_id"),  # v1 -> v2 appointment_id
        float(_value(row, "total", 0) or 0),
        _value(row, "status"),
        _value(row, "created_at"),
        _value(row, "updated_at"),
    )


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

    mappings = [("clients", "patients"), ("reservations", "appointments"), ("invoices", "invoices")]

    try:
        for source_table, target_table in mappings:
            try:
                rows = source_conn.execute(f"SELECT * FROM {source_table}").fetchall()
                moved = 0
                for row in rows:
                    before_changes = target_conn.total_changes
                    if target_table == "patients":
                        target_conn.execute(
                            "INSERT OR IGNORE INTO patients (id, first_name, last_name, phone, email, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            _build_patient_params(row),
                        )
                    elif target_table == "appointments":
                        target_conn.execute(
                            """
                            INSERT OR IGNORE INTO appointments (id, patient_id, doctor_id, appointment_at, status, notes, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            _build_appointment_params(row),
                        )
                    elif target_table == "invoices":
                        target_conn.execute(
                            """
                            INSERT OR IGNORE INTO invoices (id, patient_id, appointment_id, amount, status, created_at, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                            """,
                            _build_invoice_params(row),
                        )
                    else:
                        continue
                    moved += target_conn.total_changes - before_changes
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
    finally:
        source_conn.close()
        target_conn.close()


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