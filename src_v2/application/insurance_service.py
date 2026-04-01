import uuid
from datetime import UTC, datetime

from src_v2.application.policy import assert_permission
from src_v2.application.ports import InsuranceClaimRepository, PatientRepository
from src_v2.domain.models import InsuranceClaim
from src_v2.domain.rules import require_non_empty, require_non_negative
from src_v2.shared.result import Result


class InsuranceService:
    def __init__(self, claims: InsuranceClaimRepository, patients: PatientRepository):
        self._claims = claims
        self._patients = patients

    def create_claim(
        self,
        actor_role: str,
        patient_id: str,
        provider_name: str,
        claim_number: str,
        amount: float,
    ) -> Result[InsuranceClaim]:
        try:
            assert_permission(actor_role, "billing:write")
            require_non_empty(provider_name, "provider_name")
            require_non_empty(claim_number, "claim_number")
            require_non_negative(amount, "amount")
            if not self._patients.get(patient_id):
                return Result.failure("Patient not found")
            now = datetime.now(UTC)
            claim = InsuranceClaim(
                id=str(uuid.uuid4()),
                patient_id=patient_id,
                provider_name=provider_name.strip(),
                claim_number=claim_number.strip(),
                amount=amount,
                status="submitted",
                created_at=now,
                updated_at=now,
            )
            self._claims.create(claim)
            return Result.success(claim)
        except Exception as exc:
            return Result.failure(str(exc))

    def list_claims_for_patient(
        self,
        actor_role: str,
        patient_id: str,
        limit: int = 100,
    ) -> Result[list[InsuranceClaim]]:
        try:
            assert_permission(actor_role, "billing:read")
            require_non_empty(patient_id, "patient_id")
            return Result.success(self._claims.list_by_patient(patient_id, limit=limit))
        except Exception as exc:
            return Result.failure(str(exc))

    def set_claim_status(self, actor_role: str, claim_id: str, status: str) -> Result[bool]:
        try:
            assert_permission(actor_role, "billing:write")
            require_non_empty(claim_id, "claim_id")
            require_non_empty(status, "status")
            return Result.success(self._claims.set_status(claim_id, status.strip()))
        except Exception as exc:
            return Result.failure(str(exc))

    def delete_claim(self, actor_role: str, claim_id: str) -> Result[bool]:
        try:
            assert_permission(actor_role, "billing:write")
            require_non_empty(claim_id, "claim_id")
            return Result.success(self._claims.delete(claim_id))
        except Exception as exc:
            return Result.failure(str(exc))
