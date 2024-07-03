from .profile import (
    get_profile_router,
    create_profile_router,
    update_profile_router,
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
    get_profile_router,
    create_profile_router,
    update_profile_router,
    # echo_router,  # echo_router must be last
]

__all__ = (
    "routers_list",
)
