from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from devops_console_rest_api import models
from devops_console_rest_api.clients import user_client
from devops_console_rest_api.core import security
from devops_console_rest_api.core.config import settings

router = APIRouter()

@router.post("/login/access-token", response_model=models.Token)
def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = user_client.authenticate(
        email=EmailStr(form_data.username), password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Bad username or password")
    access_token_ttl = timedelta(minutes=settings.ACCESS_TOKEN_TTL)
    return {
        "access_token": security.create_access_token(user.uuid, ttl=access_token_ttl),
        "token_type": "bearer"
    }