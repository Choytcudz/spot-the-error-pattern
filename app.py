"""Local and AWS entry point. Serves the loop and the held-out check."""

import io

import cv2
from flask import Flask, jsonify, request, send_file

from evaluate import EXPECTED
from spot_error import make_scene, run

app = Flask(__name__)


@app.get("/health")
def health():
    return jsonify({"opencv": cv2.__version__, "service": "spot-the-error-pattern"})


@app.get("/inspect/<kind>")
def inspect(kind: str):
    if kind not in EXPECTED:
        return jsonify({"error": "unknown kind", "kinds": sorted(EXPECTED)}), 400
    seed = int(request.args.get("seed", "1000"))
    img = make_scene(seed, kind)
    return jsonify({"kind": kind, "seed": seed, "result": run(img)})


@app.post("/inspect")
def inspect_upload():
    upload = request.files.get("image")
    if upload is None:
        return jsonify({"error": "attach an image file under the name image"}), 400
    data = np_from_upload(upload.read())
    if data is None:
        return jsonify({"error": "OpenCV could not decode that file"}), 400
    return jsonify({"result": run(data)})


def np_from_upload(blob: bytes):
    import numpy as np

    arr = np.frombuffer(blob, dtype=np.uint8)
    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


@app.get("/fixture/<kind>.png")
def fixture(kind: str):
    if kind not in EXPECTED:
        return jsonify({"error": "unknown kind"}), 400
    img = make_scene(1000, kind)
    ok, encoded = cv2.imencode(".png", img)
    if not ok:
        return jsonify({"error": "encode failed"}), 500
    return send_file(io.BytesIO(encoded.tobytes()), mimetype="image/png")


@app.get("/")
def index():
    kinds = " ".join(
        f'<a href="/inspect/{k}?seed=1000">{k}</a>' for k in EXPECTED
    )
    page = f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Spot the Error Pattern</title></head>
<body>
<h1>Spot the Error Pattern</h1>
<p>OpenCV {cv2.__version__} measures a synthetic image. The measurement chooses the next action. A failed repair stops for a person.</p>
<p>{kinds}</p>
<p><a href="/health">health</a></p>
</body></html>"""
    return page


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
