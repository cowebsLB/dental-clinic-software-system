# V1 -> V2 Migration Guide

## Scope

Current migration script moves baseline tables from local v1 SQLite:

- `clients` -> `patients`
- `reservations` -> `appointments`
- `invoices` -> `invoices`

## Run

```bash
python scripts/migrate_v1_to_v2.py --source ./data/local_cache.db --target ./data/v2.db --report ./docs/migration-report.json
```

## Reconciliation

- Compare source row counts vs migrated row counts in report output.
- Review `errors` list and fix data shape mismatches.
- Verify target counts for `patients`, `appointments`, `invoices`.
