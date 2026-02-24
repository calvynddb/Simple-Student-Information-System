"""
Sort operations for Programs.
"""


class ProgramSort:
    """Sort operations for programs."""
    
    @staticmethod
    def by_field(programs, field, reverse=False):
        """Sort programs by a specific field."""
        return sorted(programs, key=lambda p: str(p.get(field, '')).lower(), reverse=reverse)
    
    @staticmethod
    def by_code(programs, reverse=False):
        """Sort programs by code."""
        return ProgramSort.by_field(programs, 'code', reverse)
    
    @staticmethod
    def by_name(programs, reverse=False):
        """Sort programs by name."""
        return ProgramSort.by_field(programs, 'name', reverse)
    
    @staticmethod
    def by_college(programs, reverse=False):
        """Sort programs by college."""
        return ProgramSort.by_field(programs, 'college', reverse)
