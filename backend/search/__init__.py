"""
Search operations for Students, Programs, and Colleges.
"""

from .students import StudentSearch
from .programs import ProgramSearch
from .colleges import CollegeSearch

__all__ = ["StudentSearch", "ProgramSearch", "CollegeSearch"]
