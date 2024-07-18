from sanic import BadRequest
import re 

class Validator:
    def __init__(self):
        self.FieldErrors = {}

    def Valid(self):
        return len(self.FieldErrors) == 0

    def AddFieldError(self, key, message):
        # Initialize the map if it's not initialized
        if not self.FieldErrors:
            self.FieldErrors = {}
        # Add error message if key doesn't exist
        if key not in self.FieldErrors:
            self.FieldErrors[key] = message

    def CheckField(self, ok, key, message):
        if not ok:
            self.AddFieldError(key, message)


class Validations(BadRequest):
    code = 400
    @staticmethod
    def is_valid_str(value, min_length=1, max_length=100) -> bool:
        try:
            return min_length <= len(value) <= max_length
        except (ValueError, TypeError):
            return False 
    
    @staticmethod
    def is_not_blank(value):
        if value != None:
            return len(str.strip(value)) > 0
        return False
    
    @staticmethod
    def is_integer(value):
        try:
            int_value = int(value)  
            return True  
        except (ValueError, TypeError):
            return False  # 
    
    @staticmethod
    def matches(value, rx):
        if re.match(rx, value):
            return True
        else:
            return False
    
    @staticmethod
    def minsymb(value, num):
        return len(value) >= num 
    
    @staticmethod
    def maxsymb(value, num):
        return len(value) <= num
