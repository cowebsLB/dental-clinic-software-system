import os
import tempfile
import unittest

from src_v2.infrastructure.container import build_services


class V2OperationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp_dir.name, "v2_ops.db")
        self.services = build_services(self.db_path)
        login = self.services.auth_service.login("admin", "admin")
        assert login.ok
        self.session = login.value

    def tearDown(self) -> None:
        self.services.close()
        self.tmp_dir.cleanup()

    def test_create_operational_resources(self) -> None:
        doctor = self.services.operations_service.create_doctor(
            actor_role=self.session.role,
            name="Dr Smith",
            specialization="Orthodontics",
        )
        self.assertTrue(doctor.ok, doctor.error)

        room = self.services.operations_service.create_room(
            actor_role=self.session.role,
            room_number="R-101",
            room_type="Procedure",
        )
        self.assertTrue(room.ok, room.error)

        equipment = self.services.operations_service.create_equipment(
            actor_role=self.session.role,
            name="X-Ray Unit",
            equipment_type="Imaging",
        )
        self.assertTrue(equipment.ok, equipment.error)


if __name__ == "__main__":
    unittest.main()
