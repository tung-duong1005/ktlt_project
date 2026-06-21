"""app.models package – re-exports all domain model classes for convenience."""

from app.models.student import Student
from app.models.schedule import Schedule
from app.models.attendance import AttendanceRecord
from app.models.session import Session
from app.models.school_class import SchoolClass

__all__ = [
    "Student",
    "Schedule",
    "AttendanceRecord",
    "Session",
    "SchoolClass",
]
