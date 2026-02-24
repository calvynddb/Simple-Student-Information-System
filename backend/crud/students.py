"""
CRUD operations for Student entity.
"""

from ..storage import save_csv
from ..validators import validate_student


class StudentCRUD:
    """CRUD operations for Student entity."""
    
    def __init__(self, students_list):
        """Initialize with reference to students data list."""
        self.data = students_list
    
    def create(self, student):
        """Create a new student."""
        ok, msg = validate_student(student)
        if not ok:
            return False, msg
        
        if any(s['id'] == student['id'] for s in self.data):
            return False, "Student ID already exists"
        
        self.data.append(student)
        save_csv('student', self.data)
        return True, "Student created"
    
    def read(self, student_id):
        """Read a student by ID."""
        return next((s for s in self.data if s['id'] == student_id), None)
    
    def update(self, student_id, updates):
        """Update a student by ID."""
        student = self.read(student_id)
        if not student:
            return False, "Student not found"
        
        student.update(updates)
        save_csv('student', self.data)
        return True, "Student updated"
    
    def delete(self, student_id):
        """Delete a student by ID."""
        student = self.read(student_id)
        if not student:
            return False, "Student not found"
        
        self.data.remove(student)
        save_csv('student', self.data)
        return True, "Student deleted"
    
    def list(self):
        """List all students."""
        return self.data.copy()
