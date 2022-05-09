from fastapi import APIRouter, Depends
from app.api import deps

from app.models.user import UserInDB


router = APIRouter()


@router.get("/", tags=["kubernetes"])
async def read_pods(
    current_user: UserInDB = Depends(deps.get_current_user)
):
    return {"message": "Hello World!"}