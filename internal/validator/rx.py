import re 

EmailRX = re.compile("^[a-zA-Z0-9.!#$%&'*+\\/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\\.[a-zA-Z0-9](?:[a-zA-Z0-9-])?)*$")
PassRX = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,25}$")

passFilt = '''
    Should have at least one number.
    Should have at least one uppercase and one lowercase character.
    Should have at least one special symbol.
    Should be between 8 to 25 characters long.
'''