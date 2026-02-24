"""
CRUD operations for Program entity.
"""

from ..storage import save_csv
from ..validators import validate_program


class ProgramCRUD:
    """CRUD operations for Program entity."""
    
    def __init__(self, programs_list):
        """Initialize with reference to programs data list."""
        self.data = programs_list
    
    def create(self, program):
        """Create a new program."""
        ok, msg = validate_program(program)
        if not ok:
            return False, msg
        
        if any(p['code'] == program['code'] for p in self.data):
            return False, "Program code already exists"
        
        self.data.append(program)
        save_csv('program', self.data)
        return True, "Program created"
    
    def read(self, program_code):
        """Read a program by code."""
        return next((p for p in self.data if p['code'] == program_code), None)
    
    def update(self, program_code, updates):
        """Update a program by code."""
        program = self.read(program_code)
        if not program:
            return False, "Program not found"
        
        program.update(updates)
        program['code'] = program_code  # Preserve code
        save_csv('program', self.data)
        return True, "Program updated"
    
    def delete(self, program_code):
        """Delete a program by code."""
        program = self.read(program_code)
        if not program:
            return False, "Program not found"
        
        self.data.remove(program)
        save_csv('program', self.data)
        return True, "Program deleted"
    
    def list(self):
        """List all programs."""
        return self.data.copy()
