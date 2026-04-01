from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class User:
    id: str
    username: str
    password_hash: str
    role: str
    is_active: bool


@dataclass(frozen=True)
class Patient:
    id: str
    first_name: str
    last_name: str
    phone: str
    email: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Appointment:
    id: str
    patient_id: str
    doctor_id: str
    appointment_at: datetime
    status: str
    notes: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class TreatmentPlan:
    id: str
    patient_id: str
    title: str
    description: str
    estimated_total: float
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Invoice:
    id: str
    patient_id: str
    appointment_id: str
    amount: float
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Doctor:
    id: str
    name: str
    specialization: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Room:
    id: str
    room_number: str
    room_type: str
    is_available: bool
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Equipment:
    id: str
    name: str
    equipment_type: str
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class Prescription:
    id: str
    patient_id: str
    doctor_id: str
    medication: str
    dosage: str
    instructions: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class ClinicalNote:
    id: str
    patient_id: str
    doctor_id: str
    note: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class InsuranceClaim:
    id: str
    patient_id: str
    provider_name: str
    claim_number: str
    amount: float
    status: str
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class SyncJob:
    id: str
    entity_type: str
    entity_id: str
    operation: str
    payload_json: str
    idempotency_key: str
    status: str
    retry_count: int
    last_error: str
    created_at: datetime
    updated_at: datetime
