# Paste this into Devpost

Account: castellanos-josephd. Draft 1266658. Deadline on the page you pasted: Oct 26, 2026, 11:45 p.m. PDT.

You still record the video and click submit. I cannot log into Devpost.

The report, the text below, the diagram, and the video become Submitted Materials. OpenCV and AWS get a broad license to those uploads. The source stays under the repository LICENSE: all rights reserved to Joseph C. Hoyt. Linking the repository does not license the source. Do not upload the source file into Devpost unless you mean to include it in that license.

Repository: https://github.com/Choytcudz/spot-the-error-pattern

## Project name

Spot the Error Pattern

## Tagline

OpenCV 5 measures a frame, picks the next action, and stops when the repair fails.

## About the project

A single vision score hides the next decision. A blurry frame and a blown-out frame need different next steps. A step that does not fix the image has to stop for a person.

The user is someone screening captured frames before those frames are treated as usable. Every demo image is drawn by the program. There are no photographs and no personal data.

OpenCV 5.0.0 (`opencv-python-headless` 5.0.0.93) records three measurements on each image: contrast-normalized Laplacian variance, mean brightness, and the fraction of pixels at or above 250.

The first measurement picks one action:

- glare fraction above 0.04: hold for a person
- brightness below 80: rescale exposure, then measure again
- blur variance below 200: sharpen, then measure again
- otherwise: accept

If the second measurement is still a repair case, or glare, the final action is hold for a person. The repair runs only because the first measurement failed. That is the agentic step. A chatbot explaining a fixed result is not this loop.

## AWS

One Amazon Linux 2023 t3.micro in us-east-1, account 943939515056, instance i-0669d7039cd2ccb83. The instance role can read s3://spot-error-943939515056/app/ and nothing else is granted by that policy. The process is python3.11 app.py on port 8080. Port 22 is closed. IMDSv2 is required.

Live page: http://54.227.35.251:8080/

This is not Graviton and COOL is not installed. The COOL prize is not claimed. Path: Agentic Vision only.

## Try it

http://54.227.35.251:8080/health

http://54.227.35.251:8080/inspect/mild_blur?seed=1000

http://54.227.35.251:8080/inspect/heavy_blur?seed=1000

http://54.227.35.251:8080/inspect/dark?seed=1000

http://54.227.35.251:8080/inspect/glare?seed=1000

Checked after boot on Oct 26, 2026. Health returned OpenCV 5.0.0. Seed 1000:

- clean: accept. Blur variance 348.948.
- mild blur: sharpen, then accept. Variance 147.612, then 312.123.
- heavy blur: sharpen, then stop. Variance 6.995, then 92.852. The repair did not clear 200.
- dark: rescale, then accept. Brightness 49.657, then 170.593.
- glare: stop on step 1. Glare fraction 0.05277.

Uploading the glare drawing to POST /inspect also stopped.

## Evaluation

evaluate.py draws 4 calibration images and 4 held-out images for each of five kinds. The blur cutoff was set from the calibration seeds. The held-out seeds were not used to pick it. On those 20 held-out drawings the final action matched the intended action 20 times: clean 4/4, mild blur 4/4, heavy blur 4/4, dark 4/4, glare 4/4.

This is the program's own drawing function, not a camera and not a public photograph set. A different drawing, or a real photo, can miss. Heavy blur is the failure the loop is built to keep.

## Source code

https://github.com/Choytcudz/spot-the-error-pattern

License: Copyright 2026 Joseph C. Hoyt. All rights reserved. Judges may view it. That view is not a license to copy or reuse the code. Do not attach the source files to the Devpost upload.

## Built with

OpenCV 5, Python, Flask, Amazon EC2, Amazon S3. Not COOL. Not a language model.

## Built-with checkboxes to select if they appear

OpenCV. Python. Amazon Web Services. Flask.

## What you upload

- REPORT.md as the technical report
- architecture.png as the diagram
- a video of 5 minutes or less

## Video, in this order, under 5 minutes

1. Your name, one person, project name, Agentic Vision, not COOL.
2. Open http://54.227.35.251:8080/health and read OpenCV 5.0.0.
3. Open mild blur, then heavy blur, then dark, then glare, all with seed 1000. Say that the first measurement chose the next action, and that heavy blur was measured again and still stopped.
4. Show architecture.png. One t3.micro, code from S3, port 8080, not Graviton.
5. Say the 20 held-out drawings matched, and that those drawings are the same generator, not photographs. Heavy blur is the kept failure.

## After judging

```bash
aws ec2 terminate-instances --region us-east-1 --instance-ids i-0669d7039cd2ccb83
```

Leave it running until you know judges will not open the URL. It is a small instance, and port 8080 is open to the internet with no login. It was launched from the root user of account 943939515056.
