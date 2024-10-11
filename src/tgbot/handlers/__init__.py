from .echo import (
    echo_router,
)
from .profile import (
    get_router,
    create_router,
    update_router,
    delete_router,
)
from .start import (
    start_router,
)
from .user import (
    user_router,
)

routers_list = [
    start_router,
    user_router,
    get_router,
    create_router,
    update_router,
    delete_router,
    echo_router,  # must be last one
]

__all__ = (
    "routers_list",
)
