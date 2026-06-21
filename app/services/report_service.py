from app.core.linked_list import MyLinkedList
from app.core.constants import AttendanceStatus
from app.models.student import Student
from app.models.session import Session
from app.models.school_class import SchoolClass


class AbsenceReportItem:
    """Helper structure storing computed absence stats for a student.

    Attributes:
        student (Student): The Student reference.
        totalSessions (int): Total recorded sessions.
        absenceCount (int): Number of absences.
        absenceRate (float): Calculated absence percentage rate.
    """

    def __init__(self, student: Student, totalSessions: int, absenceCount: int, absenceRate: float):
        """Initializes an AbsenceReportItem.

        Args:
            student (Student): The Student reference.
            totalSessions (int): Total recorded sessions.
            absenceCount (int): Number of absences.
            absenceRate (float): The absence rate.
        """
        self.student = student
        self.totalSessions = totalSessions
        self.absenceCount = absenceCount
        self.absenceRate = absenceRate


class AttendanceReport:
    """Generates attendance reports and warnings for a class."""

    def reportAttendanceBySession(self, session: Session) -> str:
        """Generates a summary string of attendance counts for a session.

        Args:
            session (Session): The session to report.

        Returns:
            str: The summary report text.
        """
        # Count present, excused, unexcused
        present = 0
        excused = 0
        unexcused = 0

        curr = session.attendanceList.head
        while curr is not None:
            status = curr.data.getStatus()
            if status == AttendanceStatus.PRESENT:
                present += 1
            elif status == AttendanceStatus.EXCUSED_ABSENCE:
                excused += 1
            elif status == AttendanceStatus.UNEXCUSED_ABSENCE:
                unexcused += 1
            curr = curr.next

        total_recorded = present + excused + unexcused
        total_enrolled = 0
        if session.school_class is not None:
            total_enrolled = session.school_class.studentList.size()

        not_recorded = total_enrolled - total_recorded

        report_str = (
            f"Attendance Report for Session Date: {session.date}\n"
            f"-----------------------------------------\n"
            f"Total Enrolled Students : {total_enrolled}\n"
            f"Present Students        : {present}\n"
            f"Excused Absences        : {excused}\n"
            f"Unexcused Absences      : {unexcused}\n"
            f"Not Yet Recorded        : {not_recorded}\n"
        )
        return report_str

    def getMostAbsentStudents(self, schoolClass: SchoolClass) -> MyLinkedList:
        """Retrieves and sorts students by their absence count in descending order.

        Args:
            schoolClass (SchoolClass): The class to analyze.

        Returns:
            MyLinkedList: A list of AbsenceReportItems sorted descending.
        """
        report_items = MyLinkedList()

        # 1. Compute rates for all students
        curr_student_node = schoolClass.studentList.head
        while curr_student_node is not None:
            student = curr_student_node.data
            studentId = student.getStudentId()

            # Count absences and sessions for this student
            totalSessions = 0
            absenceCount = 0

            curr_session_node = schoolClass.sessionList.head
            while curr_session_node is not None:
                session = curr_session_node.data
                record = session.findAttendance(studentId)
                if record is not None:
                    totalSessions += 1
                    if record.getStatus() in (AttendanceStatus.EXCUSED_ABSENCE, AttendanceStatus.UNEXCUSED_ABSENCE):
                        absenceCount += 1
                curr_session_node = curr_session_node.next

            absenceRate = 0.0 if totalSessions == 0 else (absenceCount * 100.0) / totalSessions

            item = AbsenceReportItem(student, totalSessions, absenceCount, absenceRate)
            report_items.addLast(item)
            curr_student_node = curr_student_node.next

        # 2. Sort descending by absence count (bubble sort on MyLinkedList node data)
        n = report_items.size()
        for i in range(n):
            curr = report_items.head
            while curr is not None and curr.next is not None:
                if curr.data.absenceCount < curr.next.data.absenceCount:
                    # Swap data
                    temp = curr.data
                    curr.data = curr.next.data
                    curr.next.data = temp
                curr = curr.next

        return report_items

    def getAbsenceWarningList(self, schoolClass: SchoolClass) -> MyLinkedList:
        """Retrieves students who have an absence rate > 20% sorted descending by absence count.

        Args:
            schoolClass (SchoolClass): The class to analyze.

        Returns:
            MyLinkedList: A filtered list of AbsenceReportItems.
        """
        all_items = self.getMostAbsentStudents(schoolClass)
        warning_items = MyLinkedList()

        curr = all_items.head
        while curr is not None:
            if curr.data.absenceRate > 20.0:
                warning_items.addLast(curr.data)
            curr = curr.next

        return warning_items
