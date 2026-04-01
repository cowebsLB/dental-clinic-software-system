import os
import sqlite3
import tempfile
import unittest

from scripts.migrate_v1_to_v2 import migrate
from src_v2.application.policy import assert_permission
from src_v2.shared.errors import AuthorizationError


class MigrationAndPermissionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.source = os.path.join(self.tmp_dir.name, "source.db")
        self.target = os.path.join(self.tmp_dir.name, "target.db")
        self._seed_source()

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def _seed_source(self) -> None:
        conn = sqlite3.connect(self.source)
        conn.execute(
            """
            CREATE TABLE clients (
                id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                phone TEXT,
                email TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE reservations (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                doctor_id TEXT,
                start_time_utc TEXT,
                status TEXT,
                notes TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE invoices (
                id TEXT PRIMARY KEY,
                client_id TEXT,
                reservation_id TEXT,
                total REAL,
                status TEXT,
                created_at TEXT,
                updated_at TEXT
            )
            """
        )

        conn.execute(
            "INSERT INTO clients VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("p1", "Amy", "Ng", "111", "amy@example.com", "2026-04-01", "2026-04-01"),
        )
        conn.execute(
            "INSERT INTO reservations VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            ("a1", "p1", "d1", "2026-04-01T10:00:00+00:00", "scheduled", "note", "2026-04-01", "2026-04-01"),
        )
        conn.execute(
            "INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("i1", "p1", "a1", 75.5, "pending", "2026-04-01", "2026-04-01"),
        )
        conn.commit()
        conn.close()

    def test_migration_mapping_and_counts(self) -> None:
        report1 = migrate(self.source, self.target)
        self.assertEqual(report1["tables"]["clients"]["migrated_rows"], 1)
        self.assertEqual(report1["tables"]["reservations"]["migrated_rows"], 1)
        self.assertEqual(report1["tables"]["invoices"]["migrated_rows"], 1)

        conn = sqlite3.connect(self.target)
        conn.row_factory = sqlite3.Row
        appointment = conn.execute("SELECT patient_id, appointment_at FROM appointments WHERE id = ?", ("a1",)).fetchone()
        self.assertEqual(appointment["patient_id"], "p1")
        self.assertEqual(appointment["appointment_at"], "2026-04-01T10:00:00+00:00")

        invoice = conn.execute("SELECT patient_id, appointment_id, amount FROM invoices WHERE id = ?", ("i1",)).fetchone()
        self.assertEqual(invoice["patient_id"], "p1")
        self.assertEqual(invoice["appointment_id"], "a1")
        self.assertEqual(float(invoice["amount"]), 75.5)
        conn.close()

        # Re-running should skip duplicates and report zero moved rows.
        report2 = migrate(self.source, self.target)
        self.assertEqual(report2["tables"]["clients"]["migrated_rows"], 0)
        self.assertEqual(report2["tables"]["reservations"]["migrated_rows"], 0)
        self.assertEqual(report2["tables"]["invoices"]["migrated_rows"], 0)

    def test_permission_namespaces(self) -> None:
        # Clinical actions should require clinical namespace.
        assert_permission("doctor", "clinical:write")
        with self.assertRaises(AuthorizationError):
            assert_permission("doctor", "operations:write")

        # Operations actions should require operations namespace.
        with self.assertRaises(AuthorizationError):
            assert_permission("receptionist", "operations:write")


if __name__ == "__main__":
    unittest.main()
