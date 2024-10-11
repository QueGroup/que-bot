import pathlib

from nudenet import (
    NudeDetector,
)


def classification_image(image_path: str | pathlib.Path) -> bool:
    detector = NudeDetector()
    classes = detector.detect(image_path=image_path)
    censor_classes = ["FEMALE_BREAST_EXPOSED", "FEMALE_GENITALIA_EXPOSED", "ANUS_EXPOSED", "MALE_GENITALIA_EXPOSED"]
    for class_ in classes:
        if class_.get("class") in censor_classes and class_.get("score") >= 0.5:
            return True
    return False
