from fastapi import APIRouter, Depends
from devops_console_rest_api.api import deps

from devops_console_rest_api.models.user import UserInDB


router = APIRouter()


@router.get("/", tags=["kubernetes"])
async def read_pods(
    current_user: UserInDB = Depends(deps.get_current_user)
):
    return {"message": "Hello World!"}