from passlib.context import CryptContext

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Password hash algorithm
class Hash():
  def bcrypt(self: str):
    return pwd_cxt.hash(self)
  
  def verify(self, request_password):
    return pwd_cxt.verify(request_password, self)