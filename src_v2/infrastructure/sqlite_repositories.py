import sqlite3
from datetime import UTC, datetime
from typing import Optional

from src_v2.application.ports import (
    AppointmentRepository,
    ClinicalNoteRepository,
    DoctorRepository,
    EquipmentRepository,
    InsuranceClaimRepository,
    InvoiceRepository,
    PatientRepository,
    PrescriptionRepository,
    RoomRepository,
    SyncQueueRepository,
    UserRepository,
)
from src_v2.domain.models import (
    Appointment,
    ClinicalNote,
    Doctor,
    Equipment,
    InsuranceClaim,
    Invoice,
    Patient,
    Prescription,
    Room,
    SyncJob,
    User,
)


def _iso(dt: datetime) -> str:
    return dt.isoformat()


def _from_iso(raw: str) -> datetime:
    return datetime.fromisoformat(raw)


class SqliteUserRepository(UserRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def get_by_username(self, username: str) -> Optional[User]:
        row = self._conn.execute(
            "SELECT id, username, password_hash, role, is_active FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if not row:
            return None
        return User(
            id=row["id"],
            username=row["username"],
            password_hash=row["password_hash"],
            role=row["role"],
            is_active=bool(row["is_active"]),
        )


class SqlitePatientRepository(PatientRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(self, patient: Patient) -> None:
        self._conn.execute(
            """
            INSERT INTO patients (id, first_name, last_name, phone, email, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                patient.id,
                patient.first_name,
                patient.last_name,
                patient.phone,
                patient.email,
                _iso(patient.created_at),
                _iso(patient.updated_at),
            ),
        )
        self._conn.commit()

    def get(self, patient_id: str) -> Optional[Patient]:
        row = self._conn.execute(
            "SELECT id, first_name, last_name, phone, email, created_at, updated_at FROM patients WHERE id = ?",
            (patient_id,),
        ).fetchone()
        if not row:
            return None
        return Patient(
            id=row["id"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            phone=row["phone"],
            email=row["email"],
            created_at=_from_iso(row["created_at"]),
            updated_at=_from_iso(row["updated_at"]),
        )

    def list_all(self, limit: int = 100) -> list[Patient]:
        rows = self._conn.execute(
            """
            SELECT id, first_name, last_name, phone, email, created_at, updated_at
            FROM patients
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            Patient(
                id=row["id"],
                first_name=row["first_name"],
                last_name=row["last_name"],
                phone=row["phone"],
                email=row["email"],
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def count_all(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS count FROM patients").fetchone()
        return int(row["count"]) if row else 0


class SqliteAppointmentRepository(AppointmentRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(self, appointment: Appointment) -> None:
        self._conn.execute(
            """
            INSERT INTO appointments (id, patient_id, doctor_id, appointment_at, status, notes, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                appointment.id,
                appointment.patient_id,
                appointment.doctor_id,
                _iso(appointment.appointment_at),
                appointment.status,
                appointment.notes,
                _iso(appointment.created_at),
                _iso(appointment.updated_at),
            ),
        )
        self._conn.commit()

    def get(self, appointment_id: str) -> Optional[Appointment]:
        row = self._conn.execute(
            """
            SELECT id, patient_id, doctor_id, appointment_at, status, notes, created_at, updated_at
            FROM appointments WHERE id = ?
            """,
            (appointment_id,),
        ).fetchone()
        if not row:
            return None
        return Appointment(
            id=row["id"],
            patient_id=row["patient_id"],
            doctor_id=row["doctor_id"],
            appointment_at=_from_iso(row["appointment_at"]),
            status=row["status"],
            notes=row["notes"],
            created_at=_from_iso(row["created_at"]),
            updated_at=_from_iso(row["updated_at"]),
        )

    def list_all(self, limit: int = 100) -> list[Appointment]:
        rows = self._conn.execute(
            """
            SELECT id, patient_id, doctor_id, appointment_at, status, notes, created_at, updated_at
            FROM appointments
            ORDER BY appointment_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            Appointment(
                id=row["id"],
                patient_id=row["patient_id"],
                doctor_id=row["doctor_id"],
                appointment_at=_from_iso(row["appointment_at"]),
                status=row["status"],
                notes=row["notes"],
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def count_all(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS count FROM appointments").fetchone()
        return int(row["count"]) if row else 0


class SqliteInvoiceRepository(InvoiceRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(self, invoice: Invoice) -> None:
        self._conn.execute(
            """
            INSERT INTO invoices (id, patient_id, appointment_id, amount, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                invoice.id,
                invoice.patient_id,
                invoice.appointment_id,
                invoice.amount,
                invoice.status,
                _iso(invoice.created_at),
                _iso(invoice.updated_at),
            ),
        )
        self._conn.commit()

    def get(self, invoice_id: str) -> Optional[Invoice]:
        row = self._conn.execute(
            "SELECT id, patient_id, appointment_id, amount, status, created_at, updated_at FROM invoices WHERE id = ?",
            (invoice_id,),
        ).fetchone()
        if not row:
            return None
        return Invoice(
            id=row["id"],
            patient_id=row["patient_id"],
            appointment_id=row["appointment_id"],
            amount=float(row["amount"]),
            status=row["status"],
            created_at=_from_iso(row["created_at"]),
            updated_at=_from_iso(row["updated_at"]),
        )

    def list_all(self, limit: int = 100) -> list[Invoice]:
        rows = self._conn.execute(
            """
            SELECT id, patient_id, appointment_id, amount, status, created_at, updated_at
            FROM invoices
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            Invoice(
                id=row["id"],
                patient_id=row["patient_id"],
                appointment_id=row["appointment_id"],
                amount=float(row["amount"]),
                status=row["status"],
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def count_all(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) AS count FROM invoices").fetchone()
        return int(row["count"]) if row else 0


class SqliteDoctorRepository(DoctorRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(self, doctor: Doctor) -> None:
        self._conn.execute(
            """
            INSERT INTO doctors (id, name, specialization, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                doctor.id,
                doctor.name,
                doctor.specialization,
                int(doctor.is_active),
                _iso(doctor.created_at),
                _iso(doctor.updated_at),
            ),
        )
        self._conn.commit()

    def list_all(self, limit: int = 100) -> list[Doctor]:
        rows = self._conn.execute(
            """
            SELECT id, name, specialization, is_active, created_at, updated_at
            FROM doctors
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            Doctor(
                id=row["id"],
                name=row["name"],
                specialization=row["specialization"],
                is_active=bool(row["is_active"]),
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def set_active(self, doctor_id: str, is_active: bool) -> bool:
        cursor = self._conn.execute(
            "UPDATE doctors SET is_active = ?, updated_at = ? WHERE id = ?",
            (int(is_active), _iso(datetime.now(UTC)), doctor_id),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def delete(self, doctor_id: str) -> bool:
        cursor = self._conn.execute("DELETE FROM doctors WHERE id = ?", (doctor_id,))
        self._conn.commit()
        return cursor.rowcount > 0


class SqliteRoomRepository(RoomRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(self, room: Room) -> None:
        self._conn.execute(
            """
            INSERT INTO rooms (id, room_number, room_type, is_available, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                room.id,
                room.room_number,
                room.room_type,
                int(room.is_available),
                _iso(room.created_at),
                _iso(room.updated_at),
            ),
        )
        self._conn.commit()

    def list_all(self, limit: int = 100) -> list[Room]:
        rows = self._conn.execute(
            """
            SELECT id, room_number, room_type, is_available, created_at, updated_at
            FROM rooms
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            Room(
                id=row["id"],
                room_number=row["room_number"],
                room_type=row["room_type"],
                is_available=bool(row["is_available"]),
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def set_availability(self, room_id: str, is_available: bool) -> bool:
        cursor = self._conn.execute(
            "UPDATE rooms SET is_available = ?, updated_at = ? WHERE id = ?",
            (int(is_available), _iso(datetime.now(UTC)), room_id),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def delete(self, room_id: str) -> bool:
        cursor = self._conn.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        self._conn.commit()
        return cursor.rowcount > 0


class SqliteEquipmentRepository(EquipmentRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(self, equipment: Equipment) -> None:
        self._conn.execute(
            """
            INSERT INTO equipment (id, name, equipment_type, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                equipment.id,
                equipment.name,
                equipment.equipment_type,
                equipment.status,
                _iso(equipment.created_at),
                _iso(equipment.updated_at),
            ),
        )
        self._conn.commit()

    def list_all(self, limit: int = 100) -> list[Equipment]:
        rows = self._conn.execute(
            """
            SELECT id, name, equipment_type, status, created_at, updated_at
            FROM equipment
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            Equipment(
                id=row["id"],
                name=row["name"],
                equipment_type=row["equipment_type"],
                status=row["status"],
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def set_status(self, equipment_id: str, status: str) -> bool:
        cursor = self._conn.execute(
            "UPDATE equipment SET status = ?, updated_at = ? WHERE id = ?",
            (status, _iso(datetime.now(UTC)), equipment_id),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def delete(self, equipment_id: str) -> bool:
        cursor = self._conn.execute("DELETE FROM equipment WHERE id = ?", (equipment_id,))
        self._conn.commit()
        return cursor.rowcount > 0


class SqlitePrescriptionRepository(PrescriptionRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(self, prescription: Prescription) -> None:
        self._conn.execute(
            """
            INSERT INTO prescriptions (id, patient_id, doctor_id, medication, dosage, instructions, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                prescription.id,
                prescription.patient_id,
                prescription.doctor_id,
                prescription.medication,
                prescription.dosage,
                prescription.instructions,
                _iso(prescription.created_at),
                _iso(prescription.updated_at),
            ),
        )
        self._conn.commit()

    def list_by_patient(self, patient_id: str, limit: int = 100) -> list[Prescription]:
        rows = self._conn.execute(
            """
            SELECT id, patient_id, doctor_id, medication, dosage, instructions, created_at, updated_at
            FROM prescriptions
            WHERE patient_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (patient_id, limit),
        ).fetchall()
        return [
            Prescription(
                id=row["id"],
                patient_id=row["patient_id"],
                doctor_id=row["doctor_id"],
                medication=row["medication"],
                dosage=row["dosage"],
                instructions=row["instructions"],
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def delete(self, prescription_id: str) -> bool:
        cursor = self._conn.execute("DELETE FROM prescriptions WHERE id = ?", (prescription_id,))
        self._conn.commit()
        return cursor.rowcount > 0


class SqliteClinicalNoteRepository(ClinicalNoteRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(self, note: ClinicalNote) -> None:
        self._conn.execute(
            """
            INSERT INTO clinical_notes (id, patient_id, doctor_id, note, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                note.id,
                note.patient_id,
                note.doctor_id,
                note.note,
                _iso(note.created_at),
                _iso(note.updated_at),
            ),
        )
        self._conn.commit()

    def list_by_patient(self, patient_id: str, limit: int = 100) -> list[ClinicalNote]:
        rows = self._conn.execute(
            """
            SELECT id, patient_id, doctor_id, note, created_at, updated_at
            FROM clinical_notes
            WHERE patient_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (patient_id, limit),
        ).fetchall()
        return [
            ClinicalNote(
                id=row["id"],
                patient_id=row["patient_id"],
                doctor_id=row["doctor_id"],
                note=row["note"],
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def delete(self, note_id: str) -> bool:
        cursor = self._conn.execute("DELETE FROM clinical_notes WHERE id = ?", (note_id,))
        self._conn.commit()
        return cursor.rowcount > 0


class SqliteInsuranceClaimRepository(InsuranceClaimRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def create(self, claim: InsuranceClaim) -> None:
        self._conn.execute(
            """
            INSERT INTO insurance_claims (id, patient_id, provider_name, claim_number, amount, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                claim.id,
                claim.patient_id,
                claim.provider_name,
                claim.claim_number,
                claim.amount,
                claim.status,
                _iso(claim.created_at),
                _iso(claim.updated_at),
            ),
        )
        self._conn.commit()

    def list_by_patient(self, patient_id: str, limit: int = 100) -> list[InsuranceClaim]:
        rows = self._conn.execute(
            """
            SELECT id, patient_id, provider_name, claim_number, amount, status, created_at, updated_at
            FROM insurance_claims
            WHERE patient_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (patient_id, limit),
        ).fetchall()
        return [
            InsuranceClaim(
                id=row["id"],
                patient_id=row["patient_id"],
                provider_name=row["provider_name"],
                claim_number=row["claim_number"],
                amount=float(row["amount"]),
                status=row["status"],
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def set_status(self, claim_id: str, status: str) -> bool:
        cursor = self._conn.execute(
            "UPDATE insurance_claims SET status = ?, updated_at = ? WHERE id = ?",
            (status, _iso(datetime.now(UTC)), claim_id),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def delete(self, claim_id: str) -> bool:
        cursor = self._conn.execute("DELETE FROM insurance_claims WHERE id = ?", (claim_id,))
        self._conn.commit()
        return cursor.rowcount > 0


class SqliteSyncQueueRepository(SyncQueueRepository):
    def __init__(self, conn: sqlite3.Connection):
        self._conn = conn

    def enqueue(self, job: SyncJob) -> bool:
        cursor = self._conn.execute(
            """
            INSERT OR IGNORE INTO sync_jobs (
                id, entity_type, entity_id, operation, payload_json, idempotency_key,
                status, retry_count, last_error, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                job.id,
                job.entity_type,
                job.entity_id,
                job.operation,
                job.payload_json,
                job.idempotency_key,
                job.status,
                job.retry_count,
                job.last_error,
                _iso(job.created_at),
                _iso(job.updated_at),
            ),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def list_pending(self, limit: int = 100) -> list[SyncJob]:
        rows = self._conn.execute(
            """
            SELECT id, entity_type, entity_id, operation, payload_json, idempotency_key, status,
                   retry_count, last_error, created_at, updated_at
            FROM sync_jobs
            WHERE status = 'pending'
            ORDER BY created_at ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            SyncJob(
                id=row["id"],
                entity_type=row["entity_type"],
                entity_id=row["entity_id"],
                operation=row["operation"],
                payload_json=row["payload_json"],
                idempotency_key=row["idempotency_key"],
                status=row["status"],
                retry_count=int(row["retry_count"]),
                last_error=row["last_error"],
                created_at=_from_iso(row["created_at"]),
                updated_at=_from_iso(row["updated_at"]),
            )
            for row in rows
        ]

    def mark_synced(self, job_id: str) -> bool:
        cursor = self._conn.execute(
            "UPDATE sync_jobs SET status = 'synced', updated_at = ? WHERE id = ?",
            (_iso(datetime.now(UTC)), job_id),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def mark_failed(self, job_id: str, error: str) -> bool:
        cursor = self._conn.execute(
            """
            UPDATE sync_jobs
            SET status = 'pending', retry_count = retry_count + 1, last_error = ?, updated_at = ?
            WHERE id = ?
            """,
            (error, _iso(datetime.now(UTC)), job_id),
        )
        self._conn.commit()
        return cursor.rowcount > 0
