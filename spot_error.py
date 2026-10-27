"""Spot the Error Pattern.

OpenCV 5 measures a synthetic image. The measurement picks the next action.
A repair action runs only after a failed measurement, then the image is measured again.
Glare and a repair that still fails stop for a person. Nothing here is a photograph of a person.
"""

from __future__ import annotations

import cv2
import numpy as np

LIMITS = {
    "blur_variance_min": 200.0,
    "brightness_min": 80.0,
    "glare_fraction_max": 0.04,
}

REPAIR = {
    "sharpen_and_remeasure": "blur",
    "rescale_exposure": "dark",
}


def make_scene(seed: int, kind: str) -> np.ndarray:
    rng = np.random.default_rng(seed)
    img = np.full((240, 320, 3), 210, np.uint8)
    x = int(rng.integers(30, 70))
    y = int(rng.integers(30, 60))
    cv2.rectangle(img, (x, y), (x + 180, y + 120), (30, 30, 30), 2)
    cv2.line(img, (x + 15, y + 30), (x + 160, y + 30), (20, 20, 20), 2)
    cv2.line(img, (x + 15, y + 60), (x + 120, y + 60), (20, 20, 20), 2)
    cv2.circle(img, (x + 150, y + 90), 16, (20, 20, 80), -1)
    noise = rng.integers(0, 8, img.shape, dtype=np.uint8)
    img = cv2.subtract(img, noise)
    if kind == "mild_blur":
        img = cv2.GaussianBlur(img, (9, 9), 1.6)
    elif kind == "heavy_blur":
        img = cv2.GaussianBlur(img, (31, 31), 8)
    elif kind == "dark":
        img = cv2.convertScaleAbs(img, alpha=0.25, beta=0)
    elif kind == "glare":
        cv2.circle(img, (220, 40), 36, (255, 255, 255), -1)
    elif kind != "clean":
        raise ValueError(kind)
    return img


def perceive(img: np.ndarray) -> dict:
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean = float(gray.mean())
    std = float(gray.std())
    scale = 40.0 / std if std > 1 else 1.0
    norm = cv2.convertScaleAbs(gray, alpha=scale, beta=128 - mean * scale)
    blur = float(cv2.Laplacian(norm, cv2.CV_64F).var())
    glare = float((gray >= 250).mean())
    return {
        "status": "OBSERVED",
        "blur_variance": round(blur, 3),
        "brightness": round(mean, 3),
        "glare_fraction": round(glare, 5),
    }


def choose_action(measurement: dict) -> tuple[str, str]:
    if measurement["glare_fraction"] > LIMITS["glare_fraction_max"]:
        return "hold_for_human", "glare"
    if measurement["brightness"] < LIMITS["brightness_min"]:
        return "rescale_exposure", "dark"
    if measurement["blur_variance"] < LIMITS["blur_variance_min"]:
        return "sharpen_and_remeasure", "blur"
    return "accept", "sharp_and_lit"


def apply_action(img: np.ndarray, action: str) -> np.ndarray:
    if action == "rescale_exposure":
        return cv2.convertScaleAbs(img, alpha=3.2, beta=12)
    if action == "sharpen_and_remeasure":
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]], dtype=np.float32)
        return cv2.filter2D(img, -1, kernel)
    return img


def run(img: np.ndarray) -> dict:
    first = perceive(img)
    action, reason = choose_action(first)
    trace = [
        {
            "step": 1,
            "measurement": first,
            "inference": reason,
            "action": action,
        }
    ]
    final = action
    second = None
    if action in REPAIR:
        repaired = apply_action(img, action)
        second = perceive(repaired)
        follow, follow_reason = choose_action(second)
        if follow in REPAIR or follow == "hold_for_human":
            follow = "hold_for_human"
            follow_reason = "repair_failed"
        trace.append(
            {
                "step": 2,
                "measurement": second,
                "inference": follow_reason,
                "action": follow,
            }
        )
        final = follow
    return {
        "opencv": cv2.__version__,
        "limits": LIMITS,
        "final_action": final,
        "human_required": final == "hold_for_human",
        "trace": trace,
    }
