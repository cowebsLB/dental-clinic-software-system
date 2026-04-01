from abc import ABC, abstractmethod
from typing import Optional

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


class UserRepository(ABC):
    @abstractmethod
    def get_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError


class PatientRepository(ABC):
    @abstractmethod
    def create(self, patient: Patient) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, patient_id: str) -> Optional[Patient]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[Patient]:
        raise NotImplementedError

    @abstractmethod
    def count_all(self) -> int:
        raise NotImplementedError


class AppointmentRepository(ABC):
    @abstractmethod
    def create(self, appointment: Appointment) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, appointment_id: str) -> Optional[Appointment]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[Appointment]:
        raise NotImplementedError

    @abstractmethod
    def count_all(self) -> int:
        raise NotImplementedError


class InvoiceRepository(ABC):
    @abstractmethod
    def create(self, invoice: Invoice) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, invoice_id: str) -> Optional[Invoice]:
        raise NotImplementedError

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[Invoice]:
        raise NotImplementedError

    @abstractmethod
    def count_all(self) -> int:
        raise NotImplementedError


class DoctorRepository(ABC):
    @abstractmethod
    def create(self, doctor: Doctor) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[Doctor]:
        raise NotImplementedError

    @abstractmethod
    def set_active(self, doctor_id: str, is_active: bool) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete(self, doctor_id: str) -> bool:
        raise NotImplementedError


class RoomRepository(ABC):
    @abstractmethod
    def create(self, room: Room) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[Room]:
        raise NotImplementedError

    @abstractmethod
    def set_availability(self, room_id: str, is_available: bool) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete(self, room_id: str) -> bool:
        raise NotImplementedError


class EquipmentRepository(ABC):
    @abstractmethod
    def create(self, equipment: Equipment) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self, limit: int = 100) -> list[Equipment]:
        raise NotImplementedError

    @abstractmethod
    def set_status(self, equipment_id: str, status: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete(self, equipment_id: str) -> bool:
        raise NotImplementedError


class PrescriptionRepository(ABC):
    @abstractmethod
    def create(self, prescription: Prescription) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_by_patient(self, patient_id: str, limit: int = 100) -> list[Prescription]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, prescription_id: str) -> bool:
        raise NotImplementedError


class ClinicalNoteRepository(ABC):
    @abstractmethod
    def create(self, note: ClinicalNote) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_by_patient(self, patient_id: str, limit: int = 100) -> list[ClinicalNote]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, note_id: str) -> bool:
        raise NotImplementedError


class InsuranceClaimRepository(ABC):
    @abstractmethod
    def create(self, claim: InsuranceClaim) -> None:
        raise NotImplementedError

    @abstractmethod
    def list_by_patient(self, patient_id: str, limit: int = 100) -> list[InsuranceClaim]:
        raise NotImplementedError

    @abstractmethod
    def set_status(self, claim_id: str, status: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def delete(self, claim_id: str) -> bool:
        raise NotImplementedError


class SyncQueueRepository(ABC):
    @abstractmethod
    def enqueue(self, job: SyncJob) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_pending(self, limit: int = 100) -> list[SyncJob]:
        raise NotImplementedError

    @abstractmethod
    def mark_synced(self, job_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def mark_failed(self, job_id: str, error: str) -> bool:
        raise NotImplementedError
