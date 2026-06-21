class AttendanceStatus:
    """Allowed values and validations for attendance status.

    Attributes:
        PRESENT (str): Student is present ("PRESENT").
        EXCUSED_ABSENCE (str): Student is absent with permission ("EXCUSED_ABSENCE").
        UNEXCUSED_ABSENCE (str): Student is absent without permission ("UNEXCUSED_ABSENCE").
    """
    PRESENT = "PRESENT"
    EXCUSED_ABSENCE = "EXCUSED_ABSENCE"
    UNEXCUSED_ABSENCE = "UNEXCUSED_ABSENCE"

    @classmethod
    def is_valid(cls, value: str) -> bool:
        """Validates if the status string matches one of the three allowed values.

        Args:
            value (str): The attendance status string.

        Returns:
            bool: True if valid, False otherwise.
        """
        return value in (cls.PRESENT, cls.EXCUSED_ABSENCE, cls.UNEXCUSED_ABSENCE)
