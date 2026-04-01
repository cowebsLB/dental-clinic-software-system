from dataclasses import dataclass
import sqlite3

from src_v2.application.appointment_service import AppointmentService
from src_v2.application.auth_service import AuthService
from src_v2.application.billing_service import BillingService
from src_v2.application.clinical_service import ClinicalService
from src_v2.application.insurance_service import InsuranceService
from src_v2.application.operations_service import OperationsService
from src_v2.application.patient_service import PatientService
from src_v2.application.query_service import QueryService
from src_v2.application.sync_service import SyncService
from src_v2.infrastructure.bootstrap import ensure_default_admin
from src_v2.infrastructure.sqlite_connection import connect
from src_v2.infrastructure.sqlite_repositories import (
    SqliteAppointmentRepository,
    SqliteClinicalNoteRepository,
    SqliteDoctorRepository,
    SqliteEquipmentRepository,
    SqliteInsuranceClaimRepository,
    SqliteInvoiceRepository,
    SqlitePatientRepository,
    SqlitePrescriptionRepository,
    SqliteRoomRepository,
    SqliteSyncQueueRepository,
    SqliteUserRepository,
)
from src_v2.infrastructure.sqlite_schema import initialize_schema


@dataclass(frozen=True)
class ServiceContainer:
    connection: sqlite3.Connection
    auth_service: AuthService
    patient_service: PatientService
    appointment_service: AppointmentService
    billing_service: BillingService
    operations_service: OperationsService
    clinical_service: ClinicalService
    insurance_service: InsuranceService
    query_service: QueryService
    sync_service: SyncService

    def close(self) -> None:
        self.connection.close()


def build_services(db_path: str) -> ServiceContainer:
    conn = connect(db_path)
    initialize_schema(conn)
    ensure_default_admin(conn)

    users = SqliteUserRepository(conn)
    patients = SqlitePatientRepository(conn)
    appointments = SqliteAppointmentRepository(conn)
    invoices = SqliteInvoiceRepository(conn)
    doctors = SqliteDoctorRepository(conn)
    rooms = SqliteRoomRepository(conn)
    equipment = SqliteEquipmentRepository(conn)
    prescriptions = SqlitePrescriptionRepository(conn)
    clinical_notes = SqliteClinicalNoteRepository(conn)
    insurance_claims = SqliteInsuranceClaimRepository(conn)
    sync_queue = SqliteSyncQueueRepository(conn)

    return ServiceContainer(
        connection=conn,
        auth_service=AuthService(users),
        patient_service=PatientService(patients),
        appointment_service=AppointmentService(appointments, patients),
        billing_service=BillingService(invoices, patients, appointments),
        operations_service=OperationsService(doctors, rooms, equipment),
        clinical_service=ClinicalService(prescriptions, clinical_notes, patients),
        insurance_service=InsuranceService(insurance_claims, patients),
        query_service=QueryService(patients, appointments, invoices),
        sync_service=SyncService(sync_queue),
    )
