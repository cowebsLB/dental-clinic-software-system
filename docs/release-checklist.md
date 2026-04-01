# V2 Release and Cutover Checklist

## Pre-Cutover

- [ ] Feature parity checklist reviewed (`docs/v2-feature-parity-checklist.md`)
- [ ] Backend tests pass
- [ ] Migration dry-run completed and report reviewed
- [ ] Backup of v1 local cache created

## Cutover

- [ ] Build/package v2
- [ ] Run migration against production snapshot
- [ ] Verify admin login and role behavior
- [ ] Verify patient/appointment/billing critical path

## Rollback

- [ ] Keep v1 package available
- [ ] Restore v1 database backup if rollback needed
- [ ] Document cutover outcome and incidents
