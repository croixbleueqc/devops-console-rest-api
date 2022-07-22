from fastapi import APIRouter

from .endpoints import bitbucket, k8s, websocket

router = APIRouter()

router.include_router(bitbucket.router, prefix="/bb", tags=["bitbucket"])
router.include_router(k8s.router, prefix="/k8s", tags=["kubernetes"])
router.include_router(websocket.router, prefix="/ws", tags=["websocket"])
