"""
CRUD operations for College entity.
"""

from ..storage import save_csv
from ..validators import validate_college


class CollegeCRUD:
    """CRUD operations for College entity."""
    
    def __init__(self, colleges_list):
        """Initialize with reference to colleges data list."""
        self.data = colleges_list
    
    def create(self, college):
        """Create a new college."""
        ok, msg = validate_college(college)
        if not ok:
            return False, msg
        
        if any(c['code'] == college['code'] for c in self.data):
            return False, "College code already exists"
        
        self.data.append(college)
        save_csv('college', self.data)
        return True, "College created"
    
    def read(self, college_code):
        """Read a college by code."""
        return next((c for c in self.data if c['code'] == college_code), None)
    
    def update(self, college_code, updates):
        """Update a college by code."""
        college = self.read(college_code)
        if not college:
            return False, "College not found"
        
        college.update(updates)
        college['code'] = college_code  # preserve code
        save_csv('college', self.data)
        return True, "College updated"
    
    def delete(self, college_code):
        """Delete a college by code."""
        college = self.read(college_code)
        if not college:
            return False, "College not found"
        
        self.data.remove(college)
        save_csv('college', self.data)
        return True, "College deleted"
    
    def list(self):
        """List all colleges."""
        return self.data.copy()
