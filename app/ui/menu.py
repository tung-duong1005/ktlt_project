from app.core.constants import AttendanceStatus
from app.models.student import Student
from app.models.schedule import Schedule
from app.models.school_class import SchoolClass
from app.services.attendance_manager import AttendanceManager
from app.services.report_service import AttendanceReport


class MainProgram:
    """The terminal UI presentation class handling the application menu and loop.

    Attributes:
        manager (AttendanceManager): Orchestrates core domain queries and persistence.
        report (AttendanceReport): Generates stats and sorting lists for outputs.
    """

    def __init__(self):
        """Initializes the MainProgram."""
        self.manager = AttendanceManager()
        self.report = AttendanceReport()

    def showMenu(self):
        """Prints the terminal menu interface choices to standard output."""
        print("\n===== ATTENDANCE MANAGEMENT SYSTEM =====")
        print("\nI. CLASS MANAGEMENT")
        print("1. Add a new class")
        print("2. View class list")
        print("3. Add a student to a class")
        print("4. View students in a class")
        print("5. Add/view schedule for a class")
        print("\nII. ATTENDANCE")
        print("6. Record attendance")
        print("7. Search attendance by class+date")
        print("8. Search attendance by student ID")
        print("9. View a student's absence rate")
        print("\nIII. REPORTS")
        print("10. Attendance stats for one session")
        print("11. Most-absent students")
        print("12. At-risk warning list (>20%)")
        print("\n0. Save and exit")
        print("==========================================")

    def _get_non_empty_input(self, prompt: str) -> str:
        """Prompts the user for input, repeating until a non-empty string is provided.

        Args:
            prompt (str): The prompt message to show to the user.

        Returns:
            str: The non-empty trimmed input string.
        """
        while True:
            val = input(prompt).strip()
            if val:
                return val
            print("Error: This field cannot be empty. Please try again.")

    def _get_int_input(self, prompt: str, min_val: int = None, max_val: int = None) -> int:
        """Prompts the user for an integer, repeating until a valid integer within bounds is provided.

        Args:
            prompt (str): The prompt message to show.
            min_val (int, optional): Minimum allowed value. Defaults to None.
            max_val (int, optional): Maximum allowed value. Defaults to None.

        Returns:
            int: The valid integer input.
        """
        while True:
            val_str = input(prompt).strip()
            if not val_str:
                print("Error: This field cannot be empty.")
                continue
            try:
                val = int(val_str)
                if min_val is not None and val < min_val:
                    print(f"Error: Value must be >= {min_val}.")
                    continue
                if max_val is not None and val > max_val:
                    print(f"Error: Value must be <= {max_val}.")
                    continue
                return val
            except ValueError:
                print("Error: Invalid integer input.")

    def handleChoice(self, choice: int) -> bool:
        """Triggers the appropriate manager or report actions based on the user's choice.

        Args:
            choice (int): The menu choice index (0 to 12).

        Returns:
            bool: True if the program loop should continue, False if the program should exit.
        """
        try:
            if choice == 1:
                print("\n--- Add a New Class ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                className = self._get_non_empty_input("Enter Class Name: ")
                sc = SchoolClass(classId, className)
                self.manager.addClass(sc)
                self.manager.saveData()
                print(f"Success: Class '{className}' ({classId}) added.")

            elif choice == 2:
                print("\n--- Class List ---")
                classes = self.manager.getAllClasses()
                if classes.size() == 0:
                    print("No classes registered.")
                else:
                    curr = classes.head
                    while curr is not None:
                        sc = curr.data
                        print(f"Class ID: {sc.classId} | Class Name: {sc.className}")
                        curr = curr.next

            elif choice == 3:
                print("\n--- Add Student to Class ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                sc = self.manager.findClassById(classId)
                if sc is None:
                    print(f"Error: Class with ID '{classId}' does not exist.")
                    return True
                studentId = self._get_non_empty_input("Enter Student ID: ")
                fullName = self._get_non_empty_input("Enter Student Full Name: ")
                student = Student(studentId, fullName)
                sc.addStudent(student)
                self.manager.saveData()
                print(f"Success: Student {fullName} ({studentId}) added to class {classId}.")

            elif choice == 4:
                print("\n--- View Students in Class ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                sc = self.manager.findClassById(classId)
                if sc is None:
                    print(f"Error: Class with ID '{classId}' does not exist.")
                    return True
                students = sc.getStudentList()
                if students.size() == 0:
                    print("No students enrolled in this class.")
                else:
                    print(f"Students in Class '{sc.className}' ({classId}):")
                    curr = students.head
                    while curr is not None:
                        st = curr.data
                        print(f" - Student ID: {st.getStudentId()} | Full Name: {st.getFullName()}")
                        curr = curr.next

            elif choice == 5:
                print("\n--- Add/View Schedule for Class ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                sc = self.manager.findClassById(classId)
                if sc is None:
                    print(f"Error: Class with ID '{classId}' does not exist.")
                    return True

                print("1. Add schedule entry")
                print("2. View schedule entries")
                sub_choice = self._get_int_input("Enter choice (1-2): ", 1, 2)

                if sub_choice == 1:
                    dayOfWeek = self._get_int_input("Enter Day of Week (2 for Mon, 7 for Sat, 8 for Sun): ", 2, 8)
                    period = self._get_int_input("Enter Period (1-10): ", 1, 10)
                    room = self._get_non_empty_input("Enter Room (e.g., A101): ")
                    sch = Schedule(dayOfWeek, period, room)
                    sc.addSchedule(sch)
                    self.manager.saveData()
                    print("Success: Schedule entry added.")
                elif sub_choice == 2:
                    schedules = sc.scheduleList
                    if schedules.size() == 0:
                        print("No schedule entries for this class.")
                    else:
                        print(f"Schedule for Class '{sc.className}' ({classId}):")
                        curr = schedules.head
                        day_names = {2: "Monday", 3: "Tuesday", 4: "Wednesday", 5: "Thursday", 6: "Friday", 7: "Saturday", 8: "Sunday"}
                        while curr is not None:
                            sch = curr.data
                            day_str = day_names.get(sch.dayOfWeek, f"Day {sch.dayOfWeek}")
                            print(f" - {day_str} | Period: {sch.period} | Room: {sch.room}")
                            curr = curr.next

            elif choice == 6:
                print("\n--- Record Attendance ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                date = self._get_non_empty_input("Enter Date (YYYY-MM-DD): ")
                studentId = self._get_non_empty_input("Enter Student ID: ")

                print("Select status:")
                print("1. PRESENT (Có mặt)")
                print("2. EXCUSED_ABSENCE (Vắng có phép)")
                print("3. UNEXCUSED_ABSENCE (Vắng không phép)")
                status_num = self._get_int_input("Enter choice (1-3): ", 1, 3)

                status_map = {
                    1: AttendanceStatus.PRESENT,
                    2: AttendanceStatus.EXCUSED_ABSENCE,
                    3: AttendanceStatus.UNEXCUSED_ABSENCE
                }
                status = status_map[status_num]

                self.manager.recordAttendance(classId, date, studentId, status)
                self.manager.saveData()
                print("Success: Attendance recorded.")

            elif choice == 7:
                print("\n--- Search Attendance by Class + Date ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                date = self._get_non_empty_input("Enter Date (YYYY-MM-DD): ")
                session = self.manager.searchByDate(classId, date)
                if session is None:
                    print(f"No session found for class {classId} on date {date}.")
                else:
                    print(f"Attendance for Class {classId} on {date}:")
                    curr = session.attendanceList.head
                    if curr is None:
                        print(" - No records recorded yet.")
                    while curr is not None:
                        rec = curr.data
                        print(f" - ID: {rec.student.getStudentId()} | Name: {rec.student.getFullName()} | Status: {rec.getStatus()}")
                        curr = curr.next

            elif choice == 8:
                print("\n--- Search Attendance by Student ID ---")
                studentId = self._get_non_empty_input("Enter Student ID: ")
                records = self.manager.searchByStudentId(studentId)
                if records.size() == 0:
                    print(f"No attendance history found for student {studentId}.")
                else:
                    print(f"Attendance history for student {studentId}:")
                    curr = records.head
                    while curr is not None:
                        rec = curr.data
                        print(f" - Class: {rec.classId} | Date: {rec.date} | Status: {rec.getStatus()}")
                        curr = curr.next

            elif choice == 9:
                print("\n--- View Student's Absence Rate ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                sc = self.manager.findClassById(classId)
                if sc is None:
                    print(f"Error: Class with ID '{classId}' does not exist.")
                    return True
                studentId = self._get_non_empty_input("Enter Student ID: ")
                student = sc.getStudentList().find(lambda s: s.getStudentId() == studentId)
                if student is None:
                    print(f"Error: Student '{studentId}' is not enrolled in class '{classId}'.")
                    return True
                rate = sc.calculateAbsenceRate(studentId)
                print(f"Absence rate of {student.getFullName()} ({studentId}) in class {classId}: {rate:.2f}%")

            elif choice == 10:
                print("\n--- Attendance Stats for One Session ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                sc = self.manager.findClassById(classId)
                if sc is None:
                    print(f"Error: Class with ID '{classId}' does not exist.")
                    return True
                date = self._get_non_empty_input("Enter Date (YYYY-MM-DD): ")
                session = sc.findSession(date)
                if session is None:
                    print(f"Error: Session on date '{date}' does not exist for class '{classId}'.")
                    return True
                summary = self.report.reportAttendanceBySession(session)
                print(summary)

            elif choice == 11:
                print("\n--- Most-Absent Students ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                sc = self.manager.findClassById(classId)
                if sc is None:
                    print(f"Error: Class with ID '{classId}' does not exist.")
                    return True
                report_items = self.report.getMostAbsentStudents(sc)
                if report_items.size() == 0:
                    print("No students found in this class.")
                else:
                    print(f"Most-Absent Students in Class '{sc.className}' ({classId}):")
                    curr = report_items.head
                    while curr is not None:
                        item = curr.data
                        print(f" - {item.student.getFullName()} ({item.student.getStudentId()}) | "
                              f"Sessions recorded: {item.totalSessions} | "
                              f"Absences: {item.absenceCount} | "
                              f"Rate: {item.absenceRate:.2f}%")
                        curr = curr.next

            elif choice == 12:
                print("\n--- At-Risk Warning List (>20%) ---")
                classId = self._get_non_empty_input("Enter Class ID: ")
                sc = self.manager.findClassById(classId)
                if sc is None:
                    print(f"Error: Class with ID '{classId}' does not exist.")
                    return True
                warning_items = self.report.getAbsenceWarningList(sc)
                if warning_items.size() == 0:
                    print("No students are at-risk (>20% absence rate) in this class.")
                else:
                    print(f"AT-RISK Students in Class '{sc.className}' ({classId}) with absence rate > 20%:")
                    curr = warning_items.head
                    while curr is not None:
                        item = curr.data
                        print(f" - [WARNING] {item.student.getFullName()} ({item.student.getStudentId()}) | "
                              f"Rate: {item.absenceRate:.2f}% (Absences: {item.absenceCount}/{item.totalSessions})")
                        curr = curr.next

            elif choice == 0:
                print("\nSaving data...")
                self.manager.saveData()
                print("Data saved successfully. Exiting. Goodbye!")
                return False

            else:
                print("Error: Invalid option. Please choose a menu option between 0 and 12.")

        except ValueError as ve:
            print(f"\nValidation Error: {ve}")
        except Exception as e:
            print(f"\nAn unexpected error occurred: {e}")

        return True

    def run(self):
        """Loads data, prints the menu, reads choices, and drives the handler loop."""
        print("Loading data...")
        self.manager.loadData()
        print("Data loaded successfully.")

        loop = True
        while loop:
            self.showMenu()
            choice = self._get_int_input("Please select an option (0-12): ", 0, 12)
            loop = self.handleChoice(choice)
