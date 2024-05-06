import dataclasses


@dataclasses.dataclass(eq=False)
class CancelHandler(Exception):
    title: str | None = None
