"""
Frontend UI module - all user interface components and views.
"""

from .dashboard import DashboardFrame
from .auth import LoginFrame
from .views import StudentsView, ProgramsView, CollegesView

__all__ = ["DashboardFrame", "LoginFrame", "StudentsView", "ProgramsView", "CollegesView"]
