"""Tests for domain models: Student, Schedule, SchoolClass, Session, AttendanceRecord."""

from app.core.constants import AttendanceStatus
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.attendance import AttendanceRecord
from app.models.session import Session
from app.models.school_class import SchoolClass


def test_student():
    print("Testing Student model...")
    s = Student("ST01", "John Doe")
    assert s.getStudentId() == "ST01"
    assert s.getFullName() == "John Doe"
    print("Student tests passed!")


def test_attendance_record_validation():
    print("Testing AttendanceRecord validation...")
    s = Student("ST01", "John Doe")
    rec = AttendanceRecord(s, AttendanceStatus.PRESENT)
    assert rec.getStatus() == AttendanceStatus.PRESENT

    rec.setStatus(AttendanceStatus.EXCUSED_ABSENCE)
    assert rec.getStatus() == AttendanceStatus.EXCUSED_ABSENCE

    try:
        AttendanceRecord(s, "INVALID_STATUS")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("AttendanceRecord validation tests passed!")


def test_school_class_duplicate_student():
    print("Testing SchoolClass duplicate student guard...")
    sc = SchoolClass("CS101", "Computer Science")
    s1 = Student("ST01", "John Doe")
    sc.addStudent(s1)

    try:
        sc.addStudent(Student("ST01", "Duplicate"))
        assert False, "Should have raised ValueError"
    except ValueError:
        pass
    print("SchoolClass duplicate student guard passed!")


def test_school_class_session_idempotency():
    print("Testing SchoolClass session idempotency...")
    sc = SchoolClass("CS101", "Computer Science")
    sess1 = sc.createSession("2026-06-01")
    sess2 = sc.createSession("2026-06-01")
    assert sess1 is sess2
    assert sc.sessionList.size() == 1
    print("SchoolClass session idempotency passed!")


def test_absence_rate():
    print("Testing absence rate calculation...")
    sc = SchoolClass("CS101", "Computer Science")
    s = Student("ST01", "John Doe")
    sc.addStudent(s)

    sess1 = sc.createSession("2026-06-01")
    sess2 = sc.createSession("2026-06-02")
    sess1.recordAttendance("ST01", AttendanceStatus.PRESENT)
    sess2.recordAttendance("ST01", AttendanceStatus.EXCUSED_ABSENCE)

    rate = sc.calculateAbsenceRate("ST01")
    assert rate == 50.0
    print("Absence rate calculation passed!")


if __name__ == "__main__":
    test_student()
    test_attendance_record_validation()
    test_school_class_duplicate_student()
    test_school_class_session_idempotency()
    test_absence_rate()
    print("All model tests passed!")
