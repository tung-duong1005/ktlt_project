from app.core.constants import AttendanceStatus
from app.models.student import Student


class AttendanceRecord:
    """Represents an attendance record of a student for a session.

    Attributes:
        student (Student): Injected Student reference.
        status (str): The attendance status (PRESENT, EXCUSED_ABSENCE, UNEXCUSED_ABSENCE).
        classId (str): Helper attribute for the class ID.
        date (str): Helper attribute for the session date.
    """

    def __init__(self, student: Student, status: str, classId: str = None, date: str = None):
        """Initializes an AttendanceRecord.

        Args:
            student (Student): The Student reference.
            status (str): The attendance status string.
            classId (str, optional): The class ID helper. Defaults to None.
            date (str, optional): The session date helper. Defaults to None.

        Raises:
            ValueError: If the status is not valid.
        """
        if not AttendanceStatus.is_valid(status):
            raise ValueError(f"Invalid attendance status: {status}")
        self.student = student
        self.status = status
        self.classId = classId
        self.date = date

    def getStatus(self) -> str:
        """Returns the record status.

        Returns:
            str: The attendance status.
        """
        return self.status

    def setStatus(self, status: str):
        """Sets a new attendance status.

        Args:
            status (str): The new attendance status string.

        Raises:
            ValueError: If the status is not valid.
        """
        if not AttendanceStatus.is_valid(status):
            raise ValueError(f"Invalid attendance status: {status}")
        self.status = status
