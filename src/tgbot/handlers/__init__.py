from .start import (
    start_router,
)

routers_list = [
    start_router,
    # echo_router,  # echo_router must be last
]

__all__ = (
    "routers_list",
)
