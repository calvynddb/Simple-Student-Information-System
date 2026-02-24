"""
Sort operations for Colleges.
"""


class CollegeSort:
    """Sort operations for colleges."""
    
    @staticmethod
    def by_field(colleges, field, reverse=False):
        """Sort colleges by a specific field."""
        return sorted(colleges, key=lambda c: str(c.get(field, '')).lower(), reverse=reverse)
    
    @staticmethod
    def by_code(colleges, reverse=False):
        """Sort colleges by code."""
        return CollegeSort.by_field(colleges, 'code', reverse)
    
    @staticmethod
    def by_name(colleges, reverse=False):
        """Sort colleges by name."""
        return CollegeSort.by_field(colleges, 'name', reverse)
