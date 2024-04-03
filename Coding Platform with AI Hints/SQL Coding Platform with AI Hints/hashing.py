from passlib.context import CryptContext 

# Encryption
class Hash:
    pwd = CryptContext(schemes=['bcrypt'], deprecated='auto')

    def encrypt(self, paswd: str):
        return self.pwd.hash(paswd)
    
    def verify(self, plain_password, hashed_password):
        return self.pwd.verify(plain_password, hashed_password)