from .auth import router as auth_router
from .platforms import router as platforms_router
from .content import router as content_router

__all__ = ["auth_router", "platforms_router", "content_router"]