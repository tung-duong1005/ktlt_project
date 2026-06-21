"""Tests for data persistence: save and load round-trip via AttendanceManager."""

import os
import shutil

from app.core.constants import AttendanceStatus
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.school_class import SchoolClass
from app.services.attendance_manager import AttendanceManager

# Use a dedicated temp data directory so tests don't pollute production data
_TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data_test")


def _patch_data_dir(manager: AttendanceManager, path: str):
    """Monkey-patches the _BASE_DIR used by a manager instance for isolated testing."""
    import app.services.attendance_manager as am_module
    am_module._BASE_DIR = path


def test_persistence():
    print("Testing persistence...")

    # Point the module to our test-only data directory
    import app.services.attendance_manager as am_module
    original_base = am_module._BASE_DIR
    am_module._BASE_DIR = _TEST_DATA_DIR

    try:
        # Clean up test directory if it exists from a previous run
        if os.path.exists(_TEST_DATA_DIR):
            shutil.rmtree(_TEST_DATA_DIR)

        manager = AttendanceManager()
        sc = SchoolClass("CS101", "Computer Science")
        s = Student("ST01", "John Doe")
        sc.addStudent(s)
        sch = Schedule(2, 1, "A101")
        sc.addSchedule(sch)
        sess = sc.createSession("2026-06-01")
        sess.recordAttendance("ST01", AttendanceStatus.PRESENT)

        manager.addClass(sc)
        manager.saveData()

        # Load into a new manager
        new_manager = AttendanceManager()
        new_manager.loadData()

        loaded_class = new_manager.findClassById("CS101")
        assert loaded_class is not None
        assert loaded_class.className == "Computer Science"
        assert loaded_class.studentList.size() == 1
        assert loaded_class.studentList.get(0).getFullName() == "John Doe"
        assert loaded_class.scheduleList.size() == 1
        assert loaded_class.scheduleList.get(0).room == "A101"
        assert loaded_class.sessionList.size() == 1

        loaded_sess = loaded_class.findSession("2026-06-01")
        assert loaded_sess is not None
        assert loaded_sess.attendanceList.size() == 1
        assert loaded_sess.attendanceList.get(0).getStatus() == AttendanceStatus.PRESENT

        print("Persistence tests passed!")
    finally:
        # Restore original base dir and clean up
        am_module._BASE_DIR = original_base
        if os.path.exists(_TEST_DATA_DIR):
            shutil.rmtree(_TEST_DATA_DIR)


if __name__ == "__main__":
    test_persistence()
    print("All persistence tests passed!")
