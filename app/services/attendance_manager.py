import os

from app.core.linked_list import MyLinkedList
from app.core.constants import AttendanceStatus
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.session import Session
from app.models.school_class import SchoolClass
from app.services.file_manager import FileManager
from app.services.report_service import AttendanceReport

# Resolve the data directory relative to this file's package root
_BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")


class AttendanceManager:
    """The central facade of the system orchestrating classes, records and I/O.

    Attributes:
        classList (MyLinkedList): List of all SchoolClass objects.
        fileManager (FileManager): Persistence component.
        reportGenerator (AttendanceReport): Reporting component.
    """

    def __init__(self):
        """Initializes the AttendanceManager."""
        self.classList = MyLinkedList()
        self.fileManager = FileManager()
        self.reportGenerator = AttendanceReport()

    def addClass(self, schoolClass: SchoolClass):
        """Adds a school class to the manager.

        Args:
            schoolClass (SchoolClass): The class object to add.

        Raises:
            ValueError: If the class ID already exists.
        """
        existing = self.findClassById(schoolClass.classId)
        if existing is not None:
            raise ValueError(f"Class ID {schoolClass.classId} already exists.")
        self.classList.addLast(schoolClass)

    def getAllClasses(self) -> MyLinkedList:
        """Gets all classes.

        Returns:
            MyLinkedList: List of all SchoolClass objects.
        """
        return self.classList

    def findClassById(self, classId: str) -> SchoolClass:
        """Finds a class by its ID.

        Args:
            classId (str): The class ID.

        Returns:
            SchoolClass: The matching class, or None.
        """
        return self.classList.find(lambda c: c.classId == classId)

    def recordAttendance(self, classId: str, date: str, studentId: str, status: str):
        """Records attendance status for a student in a class on a date.

        Args:
            classId (str): The class ID.
            date (str): The date of the session (YYYY-MM-DD).
            studentId (str): The student's identifier.
            status (str): The attendance status string.

        Raises:
            ValueError: If class or student is not found.
        """
        schoolClass = self.findClassById(classId)
        if schoolClass is None:
            raise ValueError(f"Class with ID {classId} not found.")

        student = schoolClass.getStudentList().find(lambda s: s.getStudentId() == studentId)
        if student is None:
            raise ValueError(f"Student with ID {studentId} is not enrolled in class {classId}.")

        session = schoolClass.findSession(date)
        if session is None:
            session = schoolClass.createSession(date)

        session.recordAttendance(studentId, status)

    def searchByDate(self, classId: str, date: str) -> Session:
        """Searches for a session in a class by date.

        Args:
            classId (str): The class ID.
            date (str): The date to search (YYYY-MM-DD).

        Returns:
            Session: The matching Session, or None.

        Raises:
            ValueError: If the class is not found.
        """
        schoolClass = self.findClassById(classId)
        if schoolClass is None:
            raise ValueError(f"Class with ID {classId} not found.")
        return schoolClass.findSession(date)

    def searchByStudentId(self, studentId: str) -> MyLinkedList:
        """Collects all attendance history records matching the student ID across all classes.

        Args:
            studentId (str): The student identifier.

        Returns:
            MyLinkedList: A list of matching AttendanceRecord objects.
        """
        result = MyLinkedList()
        curr_class_node = self.classList.head
        while curr_class_node is not None:
            school_class = curr_class_node.data
            curr_session_node = school_class.sessionList.head
            while curr_session_node is not None:
                session = curr_session_node.data
                record = session.findAttendance(studentId)
                if record is not None:
                    result.addLast(record)
                curr_session_node = curr_session_node.next
            curr_class_node = curr_class_node.next
        return result

    @staticmethod
    def _split_line(line: str) -> MyLinkedList:
        """Splits a pipe-delimited line into a MyLinkedList of field strings.

        Args:
            line (str): The raw pipe-delimited line.

        Returns:
            MyLinkedList: List of field strings.
        """
        fields = MyLinkedList()
        current = ""
        for char in line:
            if char == '|':
                fields.addLast(current)
                current = ""
            else:
                current += char
        fields.addLast(current)
        return fields

    def saveData(self):
        """Persists all current class, student, schedule, session, and attendance data to disk files."""
        classes_path = os.path.join(_BASE_DIR, "classes.txt")
        students_path = os.path.join(_BASE_DIR, "students.txt")
        schedules_path = os.path.join(_BASE_DIR, "schedules.txt")
        sessions_path = os.path.join(_BASE_DIR, "sessions.txt")
        attendance_path = os.path.join(_BASE_DIR, "attendance.txt")

        classes_content = ""
        students_content = ""
        schedules_content = ""
        sessions_content = ""
        attendance_content = ""

        curr_class_node = self.classList.head
        while curr_class_node is not None:
            sc = curr_class_node.data
            classes_content += f"{sc.classId}|{sc.className}\n"

            # Students
            curr_student = sc.studentList.head
            while curr_student is not None:
                st = curr_student.data
                students_content += f"{sc.classId}|{st.getStudentId()}|{st.getFullName()}\n"
                curr_student = curr_student.next

            # Schedules
            curr_schedule = sc.scheduleList.head
            while curr_schedule is not None:
                sch = curr_schedule.data
                schedules_content += f"{sc.classId}|{sch.dayOfWeek}|{sch.period}|{sch.room}\n"
                curr_schedule = curr_schedule.next

            # Sessions
            curr_session = sc.sessionList.head
            while curr_session is not None:
                sess = curr_session.data
                sessions_content += f"{sc.classId}|{sess.date}\n"

                # Attendance records
                curr_record = sess.attendanceList.head
                while curr_record is not None:
                    rec = curr_record.data
                    attendance_content += f"{sc.classId}|{sess.date}|{rec.student.getStudentId()}|{rec.getStatus()}\n"
                    curr_record = curr_record.next
                curr_session = curr_session.next

            curr_class_node = curr_class_node.next

        self.fileManager.writeFile(classes_path, classes_content)
        self.fileManager.writeFile(students_path, students_content)
        self.fileManager.writeFile(schedules_path, schedules_content)
        self.fileManager.writeFile(sessions_path, sessions_content)
        self.fileManager.writeFile(attendance_path, attendance_content)

    def loadData(self):
        """Loads and rebuilds classes, students, schedules, sessions, and attendance records from files."""
        if not os.path.exists(_BASE_DIR):
            os.makedirs(_BASE_DIR, exist_ok=True)

        classes_path = os.path.join(_BASE_DIR, "classes.txt")
        students_path = os.path.join(_BASE_DIR, "students.txt")
        schedules_path = os.path.join(_BASE_DIR, "schedules.txt")
        sessions_path = os.path.join(_BASE_DIR, "sessions.txt")
        attendance_path = os.path.join(_BASE_DIR, "attendance.txt")

        # Create files if they do not exist
        for path in (classes_path, students_path, schedules_path, sessions_path, attendance_path):
            if not os.path.exists(path):
                self.fileManager.writeFile(path, "")

        # 1. Load classes
        class_lines = self.fileManager.readFile(classes_path)
        curr = class_lines.head
        while curr is not None:
            fields = self._split_line(curr.data)
            if fields.size() >= 2:
                cid = fields.get(0)
                cname = fields.get(1)
                if cid and cid.strip() and cname and cname.strip():
                    sc = SchoolClass(cid, cname)
                    try:
                        self.addClass(sc)
                    except ValueError:
                        pass
            curr = curr.next

        # 2. Load students
        student_lines = self.fileManager.readFile(students_path)
        curr = student_lines.head
        while curr is not None:
            fields = self._split_line(curr.data)
            if fields.size() >= 3:
                cid = fields.get(0)
                sid = fields.get(1)
                sname = fields.get(2)
                sc = self.findClassById(cid)
                if sc is not None and sid and sid.strip() and sname and sname.strip():
                    st = Student(sid, sname)
                    try:
                        sc.addStudent(st)
                    except ValueError:
                        pass
            curr = curr.next

        # 3. Load schedules
        schedule_lines = self.fileManager.readFile(schedules_path)
        curr = schedule_lines.head
        while curr is not None:
            fields = self._split_line(curr.data)
            if fields.size() >= 4:
                cid = fields.get(0)
                day = int(fields.get(1))
                period = int(fields.get(2))
                room = fields.get(3)
                sc = self.findClassById(cid)
                if sc is not None:
                    sch = Schedule(day, period, room)
                    sc.addSchedule(sch)
            curr = curr.next

        # 4. Load sessions
        session_lines = self.fileManager.readFile(sessions_path)
        curr = session_lines.head
        while curr is not None:
            fields = self._split_line(curr.data)
            if fields.size() >= 2:
                cid = fields.get(0)
                date = fields.get(1)
                sc = self.findClassById(cid)
                if sc is not None and date and date.strip():
                    sc.createSession(date)
            curr = curr.next

        # 5. Load attendance
        attendance_lines = self.fileManager.readFile(attendance_path)
        curr = attendance_lines.head
        while curr is not None:
            fields = self._split_line(curr.data)
            if fields.size() >= 4:
                cid = fields.get(0)
                date = fields.get(1)
                sid = fields.get(2)
                status = fields.get(3)
                sc = self.findClassById(cid)
                if sc is not None:
                    sess = sc.findSession(date)
                    if sess is not None:
                        try:
                            # Rebuild record, resolving studentId -> Student object
                            sess.recordAttendance(sid, status)
                        except ValueError:
                            pass
            curr = curr.next
