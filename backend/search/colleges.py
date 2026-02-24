"""
Search operations for Colleges - search by specific fields or all fields.
"""


class CollegeSearch:
    """Search operations for colleges."""
    
    @staticmethod
    def by_field(colleges, field, query):
        """Search colleges by a specific field (case-insensitive)."""
        query_lower = query.lower()
        return [c for c in colleges if field in c and query_lower in str(c[field]).lower()]
    
    @staticmethod
    def by_code(colleges, query):
        """Search colleges by code."""
        return CollegeSearch.by_field(colleges, 'code', query)
    
    @staticmethod
    def by_name(colleges, query):
        """Search colleges by name."""
        return CollegeSearch.by_field(colleges, 'name', query)
    
    @staticmethod
    def by_any_field(colleges, query):
        """Search colleges across all fields."""
        query_lower = query.lower()
        return [c for c in colleges if any(query_lower in str(v).lower() for v in c.values())]
