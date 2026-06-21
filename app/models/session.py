from app.core.linked_list import MyLinkedList
from app.core.constants import AttendanceStatus
from app.models.attendance import AttendanceRecord


class Session:
    """Represents a specific class meeting session on a date.

    Attributes:
        date (str): The session date (YYYY-MM-DD).
        attendanceList (MyLinkedList): The list of AttendanceRecords.
        school_class (SchoolClass): Injected SchoolClass reference.
    """

    def __init__(self, date: str, school_class=None):
        """Initializes a Session.

        Args:
            date (str): The session date.
            school_class (SchoolClass, optional): The parent SchoolClass. Defaults to None.
        """
        self.date = date
        self.attendanceList = MyLinkedList()
        self.school_class = school_class

    def recordAttendance(self, studentId: str, status: str):
        """Records attendance for a student.

        Args:
            studentId (str): The student identifier.
            status (str): The attendance status.

        Raises:
            ValueError: If class context is missing, record already exists, or student not enrolled.
        """
        if self.school_class is None:
            raise ValueError("No class context to resolve student.")

        if self.findAttendance(studentId) is not None:
            raise ValueError(f"Attendance record for student {studentId} already exists in session {self.date}.")

        student = self.school_class.studentList.find(lambda s: s.getStudentId() == studentId)
        if student is None:
            raise ValueError(f"Student {studentId} is not enrolled in class {self.school_class.classId}.")

        record = AttendanceRecord(student, status, self.school_class.classId, self.date)
        self.attendanceList.addLast(record)

    def findAttendance(self, studentId: str) -> AttendanceRecord:
        """Finds the attendance record for a student by their ID.

        Args:
            studentId (str): The student ID.

        Returns:
            AttendanceRecord: The matching record, or None.
        """
        return self.attendanceList.find(lambda r: r.student.getStudentId() == studentId)

    def countPresent(self) -> int:
        """Counts the number of present students.

        Returns:
            int: The count of PRESENT students.
        """
        count = 0
        curr = self.attendanceList.head
        while curr is not None:
            if curr.data.getStatus() == AttendanceStatus.PRESENT:
                count += 1
            curr = curr.next
        return count
