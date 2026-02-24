"""
Sort operations for Students.
"""


class StudentSort:
    """Sort operations for students."""
    
    @staticmethod
    def by_field(students, field, reverse=False):
        """Sort students by a specific field."""
        return sorted(students, key=lambda s: str(s.get(field, '')).lower(), reverse=reverse)
    
    @staticmethod
    def by_id(students, reverse=False):
        """Sort students by ID."""
        return StudentSort.by_field(students, 'id', reverse)
    
    @staticmethod
    def by_firstname(students, reverse=False):
        """Sort students by first name."""
        return StudentSort.by_field(students, 'firstname', reverse)
    
    @staticmethod
    def by_lastname(students, reverse=False):
        """Sort students by last name."""
        return StudentSort.by_field(students, 'lastname', reverse)
    
    @staticmethod
    def by_year(students, reverse=False):
        """Sort students by year level."""
        return sorted(students, key=lambda s: int(s.get('year', 0)), reverse=reverse)
    
    @staticmethod
    def by_program(students, reverse=False):
        """Sort students by program."""
        return StudentSort.by_field(students, 'program', reverse)
    
    @staticmethod
    def by_college(students, reverse=False):
        """Sort students by college."""
        return StudentSort.by_field(students, 'college', reverse)
