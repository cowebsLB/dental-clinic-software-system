# V2 Architecture (Backend First)

## Layers

- `src_v2/domain`: core entities and invariant rules.
- `src_v2/application`: use-case services, permission policy, repository ports.
- `src_v2/infrastructure`: SQLite adapters, schema/bootstrap, service container.
- `src_v2/presentation`: reserved for next phase (modern UI/UX on stable contracts).

## Backend Flow

1. UI or CLI calls an application service.
2. Service validates permissions and domain rules.
3. Service persists/retrieves through repository ports.
4. Infrastructure adapters execute against SQLite (Supabase adapter planned next).

## Stability Contract

Before UI modernization starts, these service contracts are considered stable:

- `AuthService.login/logout/current_session`
- `PatientService.create_patient`
- `AppointmentService.create_appointment`
- `BillingService.create_invoice`
