import bcrypt

class Hash():
    @staticmethod
    def hash(password):
        bytes = password.encode('utf-8')  
        salt = bcrypt.gensalt() 
        hash = bcrypt.hashpw(bytes, salt) 
        return hash.decode()

    @staticmethod
    def checkPass(userPassword: str, hashed_password: str):
        bytes = userPassword.encode('utf-8')

        res = bcrypt.checkpw(hashed_password.encode(), bytes)

        return res

h = Hash()