from app.core.linked_list import MyLinkedList
from app.core.constants import AttendanceStatus
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.session import Session


class SchoolClass:
    """Represents a school class.

    Attributes:
        classId (str): The unique class identifier.
        className (str): The name of the class.
        studentList (MyLinkedList): List of Student objects.
        scheduleList (MyLinkedList): List of Schedule objects.
        sessionList (MyLinkedList): List of Session objects.
    """

    def __init__(self, classId: str, className: str):
        """Initializes a SchoolClass.

        Args:
            classId (str): The class ID.
            className (str): The class name.
        """
        self.classId = classId
        self.className = className
        self.studentList = MyLinkedList()
        self.scheduleList = MyLinkedList()
        self.sessionList = MyLinkedList()

    def addStudent(self, student: Student):
        """Enrolls a student in the class.

        Args:
            student (Student): The Student to add.

        Raises:
            ValueError: If the student ID is already enrolled.
        """
        existing = self.studentList.find(lambda s: s.getStudentId() == student.getStudentId())
        if existing is not None:
            raise ValueError(f"Student ID {student.getStudentId()} is already enrolled in class {self.classId}.")
        self.studentList.addLast(student)

    def getStudentList(self) -> MyLinkedList:
        """Gets the list of enrolled students.

        Returns:
            MyLinkedList: The list of Student objects.
        """
        return self.studentList

    def addSchedule(self, schedule: Schedule):
        """Adds a schedule entry to the class.

        Args:
            schedule (Schedule): The Schedule entry.
        """
        duplicate = self.scheduleList.find(
            lambda s: s.dayOfWeek == schedule.dayOfWeek and s.period == schedule.period and s.room == schedule.room
        )
        if duplicate is not None:
            print(f"Warning: Class {self.classId} already has schedule on day {schedule.dayOfWeek}, period {schedule.period}, room {schedule.room}.")
        self.scheduleList.addLast(schedule)

    def createSession(self, date: str) -> Session:
        """Creates a session for the class on a specific date.

        Args:
            date (str): The session date (YYYY-MM-DD).

        Returns:
            Session: The created or existing Session.
        """
        existing = self.findSession(date)
        if existing is not None:
            return existing
        session = Session(date, self)
        self.sessionList.addLast(session)
        return session

    def findSession(self, date: str) -> Session:
        """Finds a session by date.

        Args:
            date (str): The session date.

        Returns:
            Session: The matching Session, or None.
        """
        return self.sessionList.find(lambda s: s.date == date)

    def calculateAbsenceRate(self, studentId: str) -> float:
        """Calculates the absence rate for a student in this class.

        Args:
            studentId (str): The student identifier.

        Returns:
            float: The percentage absence rate (0.0 to 100.0).
        """
        totalSessions = 0
        absences = 0
        curr = self.sessionList.head
        while curr is not None:
            session = curr.data
            record = session.findAttendance(studentId)
            if record is not None:
                totalSessions += 1
                if record.getStatus() in (AttendanceStatus.EXCUSED_ABSENCE, AttendanceStatus.UNEXCUSED_ABSENCE):
                    absences += 1
            curr = curr.next

        if totalSessions == 0:
            return 0.0
        return (absences * 100.0) / totalSessions
