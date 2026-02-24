"""
Search operations for Students - search by specific fields or all fields.
"""


class StudentSearch:
    """Search operations for students."""
    
    @staticmethod
    def by_field(students, field, query):
        """Search students by a specific field (case-insensitive)."""
        query_lower = query.lower()
        return [s for s in students if field in s and query_lower in str(s[field]).lower()]
    
    @staticmethod
    def by_id(students, query):
        """Search students by ID."""
        return StudentSearch.by_field(students, 'id', query)
    
    @staticmethod
    def by_firstname(students, query):
        """Search students by first name."""
        return StudentSearch.by_field(students, 'firstname', query)
    
    @staticmethod
    def by_lastname(students, query):
        """Search students by last name."""
        return StudentSearch.by_field(students, 'lastname', query)
    
    @staticmethod
    def by_name(students, query):
        """Search students by first or last name."""
        query_lower = query.lower()
        return [s for s in students 
                if query_lower in s.get('firstname', '').lower() or 
                   query_lower in s.get('lastname', '').lower()]
    
    @staticmethod
    def by_program(students, query):
        """Search students by program."""
        return StudentSearch.by_field(students, 'program', query)
    
    @staticmethod
    def by_college(students, query):
        """Search students by college."""
        return StudentSearch.by_field(students, 'college', query)
    
    @staticmethod
    def by_any_field(students, query):
        """Search students across all fields."""
        query_lower = query.lower()
        return [s for s in students if any(query_lower in str(v).lower() for v in s.values())]
