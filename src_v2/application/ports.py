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


class AppointmentRepository(ABC):
    @abstractmethod
    def create(self, appointment: Appointment) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, appointment_id: str) -> Optional[Appointment]:
        raise NotImplementedError


class InvoiceRepository(ABC):
    @abstractmethod
    def create(self, invoice: Invoice) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, invoice_id: str) -> Optional[Invoice]:
        raise NotImplementedError


class DoctorRepository(ABC):
    @abstractmethod
    def create(self, doctor: Doctor) -> None:
        raise NotImplementedError


class RoomRepository(ABC):
    @abstractmethod
    def create(self, room: Room) -> None:
        raise NotImplementedError


class EquipmentRepository(ABC):
    @abstractmethod
    def create(self, equipment: Equipment) -> None:
        raise NotImplementedError


class PrescriptionRepository(ABC):
    @abstractmethod
    def create(self, prescription: Prescription) -> None:
        raise NotImplementedError


class ClinicalNoteRepository(ABC):
    @abstractmethod
    def create(self, note: ClinicalNote) -> None:
        raise NotImplementedError


class InsuranceClaimRepository(ABC):
    @abstractmethod
    def create(self, claim: InsuranceClaim) -> None:
        raise NotImplementedError
