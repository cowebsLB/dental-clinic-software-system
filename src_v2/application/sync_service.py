import json
import uuid
from datetime import UTC, datetime

from src_v2.application.ports import SyncQueueRepository
from src_v2.domain.models import SyncJob
from src_v2.domain.rules import require_non_empty
from src_v2.shared.result import Result


class SyncService:
    def __init__(self, queue: SyncQueueRepository):
        self._queue = queue

    def enqueue_change(
        self,
        entity_type: str,
        entity_id: str,
        operation: str,
        payload: dict,
        idempotency_key: str,
    ) -> Result[bool]:
        try:
            require_non_empty(entity_type, "entity_type")
            require_non_empty(entity_id, "entity_id")
            require_non_empty(operation, "operation")
            require_non_empty(idempotency_key, "idempotency_key")
            now = datetime.now(UTC)
            job = SyncJob(
                id=str(uuid.uuid4()),
                entity_type=entity_type.strip(),
                entity_id=entity_id.strip(),
                operation=operation.strip(),
                payload_json=json.dumps(payload, separators=(",", ":")),
                idempotency_key=idempotency_key.strip(),
                status="pending",
                retry_count=0,
                last_error="",
                created_at=now,
                updated_at=now,
            )
            # Returns False if duplicate idempotency key exists.
            return Result.success(self._queue.enqueue(job))
        except Exception as exc:
            return Result.failure(str(exc))

    def pending_jobs(self, limit: int = 100) -> Result[list[SyncJob]]:
        try:
            return Result.success(self._queue.list_pending(limit=limit))
        except Exception as exc:
            return Result.failure(str(exc))

    def mark_job_synced(self, job_id: str) -> Result[bool]:
        try:
            require_non_empty(job_id, "job_id")
            return Result.success(self._queue.mark_synced(job_id))
        except Exception as exc:
            return Result.failure(str(exc))

    def mark_job_failed(self, job_id: str, error: str) -> Result[bool]:
        try:
            require_non_empty(job_id, "job_id")
            require_non_empty(error, "error")
            return Result.success(self._queue.mark_failed(job_id, error))
        except Exception as exc:
            return Result.failure(str(exc))
