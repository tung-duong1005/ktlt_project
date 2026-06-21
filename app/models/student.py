class Student:
    """Represents a student enrolled in the system.

    Attributes:
        studentId (str): The unique identifier of the student.
        fullName (str): The full name of the student.
    """

    def __init__(self, studentId: str, fullName: str):
        """Initializes a Student.

        Args:
            studentId (str): The unique identifier of the student.
            fullName (str): The full name of the student.
        """
        self.studentId = studentId
        self.fullName = fullName

    def getStudentId(self) -> str:
        """Returns the student ID.

        Returns:
            str: The student identifier.
        """
        return self.studentId

    def getFullName(self) -> str:
        """Returns the student's full name.

        Returns:
            str: The full name.
        """
        return self.fullName
