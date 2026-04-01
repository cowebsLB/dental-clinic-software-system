import uuid
from datetime import UTC, datetime

from src_v2.application.policy import assert_permission
from src_v2.application.ports import DoctorRepository, EquipmentRepository, RoomRepository
from src_v2.domain.models import Doctor, Equipment, Room
from src_v2.domain.rules import require_non_empty
from src_v2.shared.result import Result


class OperationsService:
    def __init__(
        self,
        doctors: DoctorRepository,
        rooms: RoomRepository,
        equipment: EquipmentRepository,
    ):
        self._doctors = doctors
        self._rooms = rooms
        self._equipment = equipment

    def create_doctor(self, actor_role: str, name: str, specialization: str) -> Result[Doctor]:
        try:
            assert_permission(actor_role, "operations:write")
            require_non_empty(name, "name")
            now = datetime.now(UTC)
            doctor = Doctor(
                id=str(uuid.uuid4()),
                name=name.strip(),
                specialization=specialization.strip(),
                is_active=True,
                created_at=now,
                updated_at=now,
            )
            self._doctors.create(doctor)
            return Result.success(doctor)
        except Exception as exc:
            return Result.failure(str(exc))

    def create_room(self, actor_role: str, room_number: str, room_type: str) -> Result[Room]:
        try:
            assert_permission(actor_role, "operations:write")
            require_non_empty(room_number, "room_number")
            now = datetime.now(UTC)
            room = Room(
                id=str(uuid.uuid4()),
                room_number=room_number.strip(),
                room_type=room_type.strip(),
                is_available=True,
                created_at=now,
                updated_at=now,
            )
            self._rooms.create(room)
            return Result.success(room)
        except Exception as exc:
            return Result.failure(str(exc))

    def create_equipment(
        self,
        actor_role: str,
        name: str,
        equipment_type: str,
        status: str = "available",
    ) -> Result[Equipment]:
        try:
            assert_permission(actor_role, "operations:write")
            require_non_empty(name, "name")
            now = datetime.now(UTC)
            item = Equipment(
                id=str(uuid.uuid4()),
                name=name.strip(),
                equipment_type=equipment_type.strip(),
                status=status.strip(),
                created_at=now,
                updated_at=now,
            )
            self._equipment.create(item)
            return Result.success(item)
        except Exception as exc:
            return Result.failure(str(exc))

    def list_doctors(self, actor_role: str, limit: int = 100) -> Result[list[Doctor]]:
        try:
            assert_permission(actor_role, "operations:read")
            return Result.success(self._doctors.list_all(limit=limit))
        except Exception as exc:
            return Result.failure(str(exc))

    def list_rooms(self, actor_role: str, limit: int = 100) -> Result[list[Room]]:
        try:
            assert_permission(actor_role, "operations:read")
            return Result.success(self._rooms.list_all(limit=limit))
        except Exception as exc:
            return Result.failure(str(exc))

    def list_equipment(self, actor_role: str, limit: int = 100) -> Result[list[Equipment]]:
        try:
            assert_permission(actor_role, "operations:read")
            return Result.success(self._equipment.list_all(limit=limit))
        except Exception as exc:
            return Result.failure(str(exc))

    def set_doctor_active(self, actor_role: str, doctor_id: str, is_active: bool) -> Result[bool]:
        try:
            assert_permission(actor_role, "operations:write")
            require_non_empty(doctor_id, "doctor_id")
            return Result.success(self._doctors.set_active(doctor_id, is_active))
        except Exception as exc:
            return Result.failure(str(exc))

    def set_room_availability(self, actor_role: str, room_id: str, is_available: bool) -> Result[bool]:
        try:
            assert_permission(actor_role, "operations:write")
            require_non_empty(room_id, "room_id")
            return Result.success(self._rooms.set_availability(room_id, is_available))
        except Exception as exc:
            return Result.failure(str(exc))

    def set_equipment_status(self, actor_role: str, equipment_id: str, status: str) -> Result[bool]:
        try:
            assert_permission(actor_role, "operations:write")
            require_non_empty(equipment_id, "equipment_id")
            require_non_empty(status, "status")
            return Result.success(self._equipment.set_status(equipment_id, status.strip()))
        except Exception as exc:
            return Result.failure(str(exc))

    def delete_doctor(self, actor_role: str, doctor_id: str) -> Result[bool]:
        try:
            assert_permission(actor_role, "operations:write")
            require_non_empty(doctor_id, "doctor_id")
            return Result.success(self._doctors.delete(doctor_id))
        except Exception as exc:
            return Result.failure(str(exc))

    def delete_room(self, actor_role: str, room_id: str) -> Result[bool]:
        try:
            assert_permission(actor_role, "operations:write")
            require_non_empty(room_id, "room_id")
            return Result.success(self._rooms.delete(room_id))
        except Exception as exc:
            return Result.failure(str(exc))

    def delete_equipment(self, actor_role: str, equipment_id: str) -> Result[bool]:
        try:
            assert_permission(actor_role, "operations:write")
            require_non_empty(equipment_id, "equipment_id")
            return Result.success(self._equipment.delete(equipment_id))
        except Exception as exc:
            return Result.failure(str(exc))
