# V2 Feature Parity Checklist (Backend First)

This checklist freezes the current v1 capability scope so v2 can reach functional parity before cutover.

## Core Modules

- [ ] Clients (`modules/clients.py`, `ui/views/clients_widget.py`)
- [ ] Appointments/Reservations (`modules/reservations.py`, `ui/views/appointments_widget.py`)
- [ ] Treatment Plans (`modules/treatment_plans.py`, `ui/views/treatment_plans_widget.py`)
- [ ] Billing/Invoices (`modules/billing.py`, `ui/views/billing_widget.py`)
- [ ] Payments (`modules/payments.py`, `ui/views/payments_widget.py`)

## Clinical Modules

- [ ] Medical Records (`modules/medical_records.py`, `ui/views/medical_records_widget.py`)
- [ ] Prescriptions (`modules/prescriptions.py`, `ui/views/prescriptions_widget.py`)

## Operations Modules

- [ ] Insurance (`modules/insurance.py`, `ui/views/insurance_widget.py`)
- [ ] Doctors (`modules/doctors.py`, `ui/views/doctors_widget.py`)
- [ ] Staff (`modules/staff.py`, `ui/views/staff_widget.py`)
- [ ] Rooms (`modules/rooms.py`, `ui/views/rooms_widget.py`)
- [ ] Equipment (`modules/equipment.py`, `ui/views/equipment_widget.py`)
- [ ] Reports (`ui/views/reports_widget.py`)

## Cross-Cutting Capabilities

- [ ] Authentication/session behavior parity
- [ ] Role permission parity
- [ ] Offline queue and sync parity
- [ ] Audit and reconciliation parity
- [ ] Export/report generation parity

## Exit Criteria

- [ ] All backend service contracts are implemented in `src_v2`
- [ ] Migration dry-run succeeds against a v1 snapshot
- [ ] Critical-flow automated tests pass
- [ ] UAT role-based scenarios pass
- [ ] Cutover + rollback checklist signed off
