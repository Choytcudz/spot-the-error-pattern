"""Local and AWS entry point. Serves the loop and the held-out check."""

import io
import random
import secrets
from html import escape

import cv2
from flask import Flask, jsonify, request, send_file

from evaluate import EXPECTED
from spot_error import REPAIR, apply_action, make_scene, run

app = Flask(__name__)

# token -> (kind, seed). The page must not reveal the kind before the person chooses.
SCENES: dict[str, tuple[str, int]] = {}
CHOICE_LABEL = {
    "usable": "it is usable",
    "blurry": "it is too blurry",
    "dark": "it is too dark",
    "glare": "it has glare",
}
FINDING_LABEL = {
    "sharp_and_lit": "usable",
    "blur": "too blurry",
    "dark": "too dark",
    "glare": "glare",
}


def remember_scene() -> str:
    if len(SCENES) > 300:
        for old in list(SCENES)[:100]:
            SCENES.pop(old, None)
    token = secrets.token_urlsafe(8)
    kind = random.choice(tuple(EXPECTED))
    seed = random.randint(1, 1_000_000)
    SCENES[token] = (kind, seed)
    return token


def png_bytes(img) -> bytes:
    ok, encoded = cv2.imencode(".png", img)
    if not ok:
        raise RuntimeError("encode failed")
    return encoded.tobytes()


def page(body: str) -> str:
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Spot the Error Pattern</title>
<style>
body {{ font-family: system-ui, sans-serif; max-width: 760px; margin: 32px auto; padding: 0 16px; color: #111; }}
img {{ width: min(100%, 640px); height: auto; border: 2px solid #111; background: #fff; }}
form {{ margin: 16px 0 28px; }}
button {{ font-size: 18px; padding: 12px 16px; margin: 0 8px 8px 0; cursor: pointer; }}
.result {{ border-left: 4px solid #111; padding: 4px 0 4px 16px; }}
a.again {{ display: inline-block; margin-top: 20px; font-size: 18px; }}
</style></head><body>
{body}
</body></html>"""


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
    seed = int(request.args.get("seed", "1000"))
    img = make_scene(seed, kind)
    return send_file(io.BytesIO(png_bytes(img)), mimetype="image/png")


@app.get("/frame/<token>.png")
def frame(token: str):
    found = SCENES.get(token)
    if found is None:
        return jsonify({"error": "that frame expired"}), 404
    kind, seed = found
    return send_file(io.BytesIO(png_bytes(make_scene(seed, kind))), mimetype="image/png")


@app.get("/")
def index():
    token = remember_scene()
    buttons = " ".join(
        f'<button name="choice" value="{key}">{escape(label)}</button>'
        for key, label in (
            ("usable", "It is usable"),
            ("blurry", "Too blurry"),
            ("dark", "Too dark"),
            ("glare", "Glare"),
        )
    )
    body = f"""
<h1>Spot the Error Pattern</h1>
<p>Look at this frame. Pick what is wrong with it. The program then measures it and either repairs it or stops.</p>
<img src="/frame/{token}.png" alt="synthetic frame">
<form method="post" action="/decide">
<input type="hidden" name="token" value="{token}">
{buttons}
</form>"""
    return page(body)


@app.post("/decide")
def decide():
    token = request.form.get("token", "")
    choice = request.form.get("choice", "")
    found = SCENES.get(token)
    if found is None or choice not in CHOICE_LABEL:
        return page("<h1>That frame expired</h1><p><a href='/'>Get another frame</a></p>"), 400
    kind, seed = found
    img = make_scene(seed, kind)
    result = run(img)
    first = result["trace"][0]
    measurement = first["measurement"]
    lines = [
        f"You said {escape(CHOICE_LABEL[choice])}.",
        (
            f"OpenCV measured blur {measurement['blur_variance']}, "
            f"brightness {measurement['brightness']}, "
            f"glare {measurement['glare_fraction']}."
        ),
    ]
    finding = FINDING_LABEL[first["inference"]]
    user_finding = {"usable": "usable", "blurry": "too blurry", "dark": "too dark", "glare": "glare"}[choice]
    if user_finding == finding:
        lines.append(f"Your call matched the measurement. The frame is {escape(finding)}.")
    else:
        lines.append(
            f"Your call did not match. The measurement says the frame is {escape(finding)}."
        )
    images = f'<img src="/frame/{token}.png" alt="frame you judged">'
    action = first["action"]
    if action in REPAIR and len(result["trace"]) > 1:
        second = result["trace"][1]
        verb = "sharpened it" if action == "sharpen_and_remeasure" else "rescaled the exposure"
        lines.append(f"Because of that measurement, the program {verb} and measured again.")
        sm = second["measurement"]
        lines.append(
            f"Second measurement: blur {sm['blur_variance']}, "
            f"brightness {sm['brightness']}, glare {sm['glare_fraction']}."
        )
        if result["final_action"] == "accept":
            lines.append("The repair cleared the cutoff. The frame is accepted.")
        else:
            lines.append(
                "The repair did not clear the cutoff. The program stops for a person. The frame is not marked usable."
            )
        images += (
            "<p>After the repair:</p>"
            f'<img src="/repaired/{token}.png" alt="frame after the repair">'
        )
    elif result["final_action"] == "hold_for_human":
        lines.append("The program does not try a repair. It stops for a person.")
    else:
        lines.append("The program accepts the frame. No repair, and no person needed.")
    text = "".join(f"<p>{line}</p>" for line in lines)
    body = f"""
<h1>Spot the Error Pattern</h1>
{images}
<div class="result">{text}</div>
<a class="again" href="/">Another frame</a>"""
    return page(body)


@app.get("/repaired/<token>.png")
def repaired(token: str):
    found = SCENES.get(token)
    if found is None:
        return jsonify({"error": "that frame expired"}), 404
    kind, seed = found
    img = make_scene(seed, kind)
    result = run(img)
    action = result["trace"][0]["action"]
    if action not in REPAIR:
        return jsonify({"error": "this frame was not repaired"}), 404
    return send_file(io.BytesIO(png_bytes(apply_action(img, action))), mimetype="image/png")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
