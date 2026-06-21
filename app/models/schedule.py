class Schedule:
    """Represents a class schedule entry.

    Attributes:
        dayOfWeek (int): Day of the week (2=Monday, 8=Sunday).
        period (int): Period index of the day.
        room (str): Classroom designation.
    """

    def __init__(self, dayOfWeek: int, period: int, room: str):
        """Initializes a Schedule.

        Args:
            dayOfWeek (int): Day of the week (2=Monday, 8=Sunday).
            period (int): Period index of the day.
            room (str): Classroom designation.
        """
        self.dayOfWeek = dayOfWeek
        self.period = period
        self.room = room
