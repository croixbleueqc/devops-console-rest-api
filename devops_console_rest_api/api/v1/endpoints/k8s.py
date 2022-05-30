from fastapi import APIRouter, Depends

router = APIRouter()


@router.get("/", tags=["kubernetes"])
async def read_pods():
    return {"message": "Hello World!"}
