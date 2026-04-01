import os
import tempfile
import unittest

from src_v2.infrastructure.container import build_services


class V2SyncServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "v2_sync.db")
        self.services = build_services(self.db_path)

    def tearDown(self) -> None:
        self.services.close()
        self.tmp_dir.cleanup()

    def test_idempotent_enqueue_and_retry_markers(self) -> None:
        first = self.services.sync_service.enqueue_change(
            entity_type="patient",
            entity_id="p-1",
            operation="update",
            payload={"email": "a@example.com"},
            idempotency_key="patient:p-1:update:1",
        )
        self.assertTrue(first.ok and first.value)

        duplicate = self.services.sync_service.enqueue_change(
            entity_type="patient",
            entity_id="p-1",
            operation="update",
            payload={"email": "a@example.com"},
            idempotency_key="patient:p-1:update:1",
        )
        self.assertTrue(duplicate.ok)
        self.assertFalse(duplicate.value)

        pending = self.services.sync_service.pending_jobs(limit=10)
        self.assertTrue(pending.ok, pending.error)
        self.assertEqual(len(pending.value), 1)
        job = pending.value[0]
        self.assertEqual(job.retry_count, 0)
        self.assertEqual(job.status, "pending")

        failed = self.services.sync_service.mark_job_failed(job.id, "network timeout")
        self.assertTrue(failed.ok and failed.value)
        pending_after_fail = self.services.sync_service.pending_jobs(limit=10)
        self.assertTrue(pending_after_fail.ok)
        self.assertEqual(len(pending_after_fail.value), 1)
        self.assertEqual(pending_after_fail.value[0].retry_count, 1)
        self.assertEqual(pending_after_fail.value[0].last_error, "network timeout")

        synced = self.services.sync_service.mark_job_synced(job.id)
        self.assertTrue(synced.ok and synced.value)
        pending_after_sync = self.services.sync_service.pending_jobs(limit=10)
        self.assertTrue(pending_after_sync.ok)
        self.assertEqual(len(pending_after_sync.value), 0)


if __name__ == "__main__":
    unittest.main()
