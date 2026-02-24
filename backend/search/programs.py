"""
Search operations for Programs - search by specific fields or all fields.
"""


class ProgramSearch:
    """Search operations for programs."""
    
    @staticmethod
    def by_field(programs, field, query):
        """Search programs by a specific field (case-insensitive)."""
        query_lower = query.lower()
        return [p for p in programs if field in p and query_lower in str(p[field]).lower()]
    
    @staticmethod
    def by_code(programs, query):
        """Search programs by code."""
        return ProgramSearch.by_field(programs, 'code', query)
    
    @staticmethod
    def by_name(programs, query):
        """Search programs by name."""
        return ProgramSearch.by_field(programs, 'name', query)
    
    @staticmethod
    def by_college(programs, query):
        """Search programs by college."""
        return ProgramSearch.by_field(programs, 'college', query)
    
    @staticmethod
    def by_any_field(programs, query):
        """Search programs across all fields."""
        query_lower = query.lower()
        return [p for p in programs if any(query_lower in str(v).lower() for v in p.values())]
