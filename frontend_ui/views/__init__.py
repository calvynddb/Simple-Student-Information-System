"""
Views module - entity-specific views for Students, Programs, Colleges.
"""

from .students import StudentsView
from .programs import ProgramsView
from .colleges import CollegesView

__all__ = ["StudentsView", "ProgramsView", "CollegesView"]
