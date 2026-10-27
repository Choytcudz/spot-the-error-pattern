# Spot the Error Pattern

Team: Joseph Castellanos Hoyt (`castellanos-josephd`). One person. Path: Agentic Vision. Not the COOL prize.

Source, all rights reserved: https://github.com/Choytcudz/spot-the-error-pattern

The contest license covers this report if it is uploaded. It does not cover the source code merely because this report names the repository.

## Problem

A single vision score hides the next decision. A blurry frame and a blown-out frame need different next steps, and a step that does not fix the image has to stop for a person.

## Users

Someone reviewing a batch of captured frames before those frames are treated as usable. The demo uses drawings made by the program, so the behavior can be checked without anyone's photo.

## What OpenCV 5 does

`opencv-python-headless` 5.0.0.93. `cv2.__version__` is 5.0.0.

For each image the program records three measurements:

- contrast-normalized Laplacian variance, for blur
- mean brightness
- fraction of pixels at or above 250, for glare

The first measurement picks one action:

- glare above 0.04: `hold_for_human`
- brightness below 80: `rescale_exposure`, then measure again
- blur variance below 200: `sharpen_and_remeasure`, then measure again
- otherwise: `accept`

A second measurement that is still a repair case or glare becomes `hold_for_human`. The repair tool is called only because the first measurement failed.

## Evaluation

`evaluate.py` draws 4 calibration images and 4 held-out images for each of five kinds. The blur cutoff was set from the calibration seed series. The held-out seeds were not used to pick it. On those 20 held-out drawings the final action matched the intended action 20 times.

| Kind | Intended final action | Held-out matches |
|---|---|---|
| clean | accept on the first measurement | 4/4 |
| mild_blur | sharpen, then accept | 4/4 |
| heavy_blur | sharpen, then stop for a person | 4/4 |
| dark | rescale, then accept | 4/4 |
| glare | stop on the first measurement | 4/4 |

This is the program's own drawing function, not a camera and not a public photograph set. A different drawing, or a real photo, can miss. Heavy blur is the failure the loop is built to keep: sharpening raises the variance and the frame is still rejected.

## AWS

One Amazon Linux 2023 `t3.micro` in `us-east-1` on account `943939515056`. Instance `i-0669d7039cd2ccb83`. Public URL on 2026-10-26: `http://54.227.35.251:8080/`. The instance role can read `s3://spot-error-943939515056/app/`. Port 8080 is open. Port 22 is not. The process is `python3.11 app.py`.

Checked from this machine after boot: `/health` returned OpenCV 5.0.0. Seed 1000 produced the five intended traces (accept; sharpen then accept; sharpen then stop; rescale then accept; stop for glare). Uploading the glare drawing to `POST /inspect` stopped for a person. Architecture drawing: `architecture.png`.

COOL is not installed. The instance is not Graviton. The COOL prize is not claimed.

## Responsible use

Synthetic rectangles and lines only. No face, no customer image, no stored upload beyond the request that measured it. A frame the repair cannot fix is not marked usable.

## Not in this entry

No five-minute video yet. No COOL benchmark. The Devpost form still has to be submitted by the account holder.
