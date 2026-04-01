# Dental Clinic Software System

## Overview

Dental clinic management system currently transitioning to a backend-first v2 architecture.

## Features

- Patient management
- Appointment scheduling
- Treatment planning
- Billing and payments
- Clinical records and prescriptions
- Staff/doctor/room/equipment operations

## Setup

1. Install dependencies:
   - `pip install -r requirements.txt`
2. Run current app:
   - `python main.py`
3. Build v2 backend baseline:
   - import from `src_v2.infrastructure.container` and call `build_services(...)`

## Usage

- v1 remains active while v2 backend is rebuilt in `src_v2`.
- Migration helper: `python scripts/migrate_v1_to_v2.py --help`

## Tech Stack

- Python
- PySide6 (desktop UI)
- SQLite (local cache)
- Supabase (remote sync/auth in supported modes)

## Documentation

- `docs/architecture.md`
- `docs/v2-feature-parity-checklist.md`
- `docs/migration.md`
- `docs/release-checklist.md`
