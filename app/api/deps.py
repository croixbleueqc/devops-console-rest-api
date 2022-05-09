from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
# from fastapi.security.oauth2 import OAuth2AuthorizationCodeBearer
from jose import JWTError, jwt
from pydantic import ValidationError

from app.core import security
from app.core.config import settings
from app.clients import user_client
from app.models import UserInDB, TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    # tokenUrl=f"{settings.API_V1_STR}/login/access-token"
    tokenUrl='https://bitbucket.org/site/oauth2/access_token'
)

# client_id = 'A8ujY6KxneHkj4Akwh'
# code = OAuth2AuthorizationCodeBearer(
#     authorizationUrl=f'https://bitbucket.org/site/oauth2/authorize?client_id={client_id}&response_type=code',

# )


def get_current_user(token: str = Depends(reusable_oauth2)) -> UserInDB:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        print(JWTError, ValidationError)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )

    user = user_client.get_by_id(token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
