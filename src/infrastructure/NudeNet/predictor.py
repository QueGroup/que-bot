import pathlib
from typing import Any

from nudenet import (
    NudeDetector,
)

detector = NudeDetector()


async def classification_image(image_path: str | pathlib.Path) -> list[dict[str, Any]]:
    return detector.detect(image_path=image_path)


async def generate_censored_image(
        image_path: str | pathlib.Path, out_path: str | pathlib.Path
) -> None:
    detector.censor(
        image_path=image_path,
        output_path=out_path,
    )
