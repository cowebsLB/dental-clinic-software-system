# Backend Core Modules (v2)

## Auth and Roles

- `src_v2/application/auth_service.py`
- `src_v2/application/policy.py`
- Role model: `admin`, `doctor`, `staff`, `receptionist`

## Patients

- Service: `src_v2/application/patient_service.py`
- Repository contract: `PatientRepository`

## Appointments

- Service: `src_v2/application/appointment_service.py`
- Repository contract: `AppointmentRepository`

## Billing

- Service: `src_v2/application/billing_service.py`
- Repository contract: `InvoiceRepository`

## Operations (Secondary Backend Phase)

- Service: `src_v2/application/operations_service.py`
- Repository contracts: `DoctorRepository`, `RoomRepository`, `EquipmentRepository`

## Clinical + Insurance (Secondary Backend Phase)

- Services:
  - `src_v2/application/clinical_service.py`
  - `src_v2/application/insurance_service.py`
- Repository contracts:
  - `PrescriptionRepository`
  - `ClinicalNoteRepository`
  - `InsuranceClaimRepository`

## Query Layer (Read APIs)

- Service:
  - `src_v2/application/query_service.py`
- Capabilities:
  - list patients/appointments/invoices
  - dashboard metrics for totals and outstanding invoices
- Purpose:
  - provide stable backend read contracts for upcoming UI/UX modernization.

## Secondary Module Query Coverage

- OperationsService read contracts:
  - `list_doctors`
  - `list_rooms`
  - `list_equipment`
- ClinicalService read contracts:
  - `list_prescriptions_for_patient`
  - `list_clinical_notes_for_patient`
- InsuranceService read contracts:
  - `list_claims_for_patient`

## Secondary Module CRUD Coverage

- OperationsService write/update/delete contracts:
  - `set_doctor_active`, `set_room_availability`, `set_equipment_status`
  - `delete_doctor`, `delete_room`, `delete_equipment`
- ClinicalService delete contracts:
  - `delete_prescription`, `delete_clinical_note`
- InsuranceService write/delete contracts:
  - `set_claim_status`, `delete_claim`

## Sync and Reliability Foundation

- Service:
  - `src_v2/application/sync_service.py`
- Backing store:
  - `sync_jobs` table in `src_v2/infrastructure/sqlite_schema.py`
  - `SqliteSyncQueueRepository` in `src_v2/infrastructure/sqlite_repositories.py`
- Reliability behaviors:
  - idempotent enqueue via unique `idempotency_key`
  - pending job listing for worker loops
  - retry accounting (`retry_count`) and `last_error` capture
  - status transitions (`pending` -> `synced`)
