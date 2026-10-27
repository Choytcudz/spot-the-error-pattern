"""Draw architecture.png. Boxes only. No photograph."""

import cv2
import numpy as np

W, H = 1100, 520
img = np.full((H, W, 3), 248, np.uint8)

def box(x, y, w, h, title, lines):
    cv2.rectangle(img, (x, y), (x + w, y + h), (30, 30, 30), 2)
    cv2.rectangle(img, (x, y), (x + w, y + 36), (30, 30, 30), -1)
    cv2.putText(img, title, (x + 12, y + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (248, 248, 248), 1, cv2.LINE_AA)
    for i, line in enumerate(lines):
        cv2.putText(img, line, (x + 12, y + 62 + i * 24), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (20, 20, 20), 1, cv2.LINE_AA)

def arrow(x1, y1, x2, y2):
    cv2.arrowedLine(img, (x1, y1), (x2, y2), (30, 30, 30), 2, tipLength=0.08)

box(30, 200, 240, 140, "Browser or curl", ["GET /inspect/<kind>", "POST /inspect image", "port 8080"])
box(360, 110, 280, 150, "EC2 t3.micro", ["Amazon Linux 2023", "us-east-1", "role reads S3 only", "not Graviton, not COOL"])
box(360, 310, 280, 160, "OpenCV 5.0.0 loop", ["measure blur, light, glare", "repair only if needed", "measure again", "else hold for a person"])
box(740, 200, 330, 150, "S3 app bucket", ["spot-error-943939515056", "pinned requirements", "user-data syncs /opt/spot"])

arrow(270, 240, 360, 180)
arrow(270, 290, 360, 370)
arrow(740, 250, 642, 185)
cv2.putText(img, "Spot the Error Pattern", (30, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (20, 20, 20), 2, cv2.LINE_AA)
cv2.putText(
    img,
    "Synthetic drawings. The measurement chooses the next action.",
    (30, 84),
    cv2.FONT_HERSHEY_SIMPLEX,
    0.55,
    (20, 20, 20),
    1,
    cv2.LINE_AA,
)
cv2.imwrite("architecture.png", img)
print("wrote architecture.png", img.shape)
