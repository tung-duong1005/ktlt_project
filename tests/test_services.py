"""Tests for AttendanceReport service: sorting and warning list logic."""

from app.core.constants import AttendanceStatus
from app.models.student import Student
from app.models.school_class import SchoolClass
from app.services.report_service import AttendanceReport


def test_business_rules_and_sorting():
    print("Testing business rules & sorting...")
    sc = SchoolClass("CS101", "Computer Science")

    s1 = Student("ST01", "John Doe")
    s2 = Student("ST02", "Jane Smith")
    s3 = Student("ST03", "Bob Johnson")

    sc.addStudent(s1)
    sc.addStudent(s2)
    sc.addStudent(s3)

    # Create sessions and record attendance
    sess1 = sc.createSession("2026-06-01")
    sess2 = sc.createSession("2026-06-02")
    sess3 = sc.createSession("2026-06-03")
    sess4 = sc.createSession("2026-06-04")
    sess5 = sc.createSession("2026-06-05")

    # ST01: 5 sessions, 1 absence -> 20.0% rate
    sess1.recordAttendance("ST01", AttendanceStatus.PRESENT)
    sess2.recordAttendance("ST01", AttendanceStatus.PRESENT)
    sess3.recordAttendance("ST01", AttendanceStatus.PRESENT)
    sess4.recordAttendance("ST01", AttendanceStatus.PRESENT)
    sess5.recordAttendance("ST01", AttendanceStatus.EXCUSED_ABSENCE)

    # ST02: 5 sessions, 2 absences -> 40.0% rate (> 20.0% - warning)
    sess1.recordAttendance("ST02", AttendanceStatus.PRESENT)
    sess2.recordAttendance("ST02", AttendanceStatus.UNEXCUSED_ABSENCE)
    sess3.recordAttendance("ST02", AttendanceStatus.PRESENT)
    sess4.recordAttendance("ST02", AttendanceStatus.EXCUSED_ABSENCE)
    sess5.recordAttendance("ST02", AttendanceStatus.PRESENT)

    # ST03: 5 sessions, 0 absences -> 0.0% rate
    sess1.recordAttendance("ST03", AttendanceStatus.PRESENT)
    sess2.recordAttendance("ST03", AttendanceStatus.PRESENT)
    sess3.recordAttendance("ST03", AttendanceStatus.PRESENT)
    sess4.recordAttendance("ST03", AttendanceStatus.PRESENT)
    sess5.recordAttendance("ST03", AttendanceStatus.PRESENT)

    # Verify rate calculations
    assert sc.calculateAbsenceRate("ST01") == 20.0
    assert sc.calculateAbsenceRate("ST02") == 40.0
    assert sc.calculateAbsenceRate("ST03") == 0.0

    # Test warnings
    report = AttendanceReport()
    warnings = report.getAbsenceWarningList(sc)
    # Only ST02 should be in warning (>20%)
    assert warnings.size() == 1
    assert warnings.get(0).student.getStudentId() == "ST02"

    # Test sorting (ST02 has 2, ST01 has 1, ST03 has 0 absences)
    sorted_items = report.getMostAbsentStudents(sc)
    assert sorted_items.size() == 3
    assert sorted_items.get(0).student.getStudentId() == "ST02"
    assert sorted_items.get(1).student.getStudentId() == "ST01"
    assert sorted_items.get(2).student.getStudentId() == "ST03"
    print("Business rules & sorting tests passed!")


if __name__ == "__main__":
    test_business_rules_and_sorting()
    print("All service tests passed!")
