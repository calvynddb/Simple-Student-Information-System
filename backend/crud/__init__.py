"""
CRUD operations for Students, Programs, and Colleges.
"""

from .students import StudentCRUD
from .programs import ProgramCRUD
from .colleges import CollegeCRUD

__all__ = ["StudentCRUD", "ProgramCRUD", "CollegeCRUD"]
