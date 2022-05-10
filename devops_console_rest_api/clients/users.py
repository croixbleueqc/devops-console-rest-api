from uuid import UUID
from pydantic import EmailStr
from devops_console_rest_api.models.user import User, UserInDB
from devops_console_rest_api.server_stubs import UserServerStub


server = UserServerStub()

class UserDBClient:
    def __init__(self):
        self.model = UserInDB

    def get_by_email(self, email: EmailStr) -> UserInDB | None:
       return server.get_user(email=email)
    
    def get_by_id(self, id: UUID) -> UserInDB | None:
        return server.get_user(uuid=id)
    
    def authenticate(self, email: EmailStr, password: str) -> UserInDB | None:
        user = self.get_by_email(email=email)
        if not user:
            return None
        if not server.verify_user(user, password):
            return None
        return user

user_client = UserDBClient()