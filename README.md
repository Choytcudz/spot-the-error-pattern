# Spot the Error Pattern

Repository: https://github.com/Choytcudz/spot-the-error-pattern

OpenCV 5.0.0 measures a synthetic image. That measurement chooses the next action. A repair is measured again. Glare, and a repair that is still bad, stop for a person.

The images are drawn by the program. There are no photographs and no personal data.

## Run locally

```bash
python3.14 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python evaluate.py
.venv/bin/python app.py
```

Open http://127.0.0.1:8080/

## Judge checks

Live on 2026-10-26, instance `i-0669d7039cd2ccb83`, public address `54.227.35.251`:

```bash
curl -s http://54.227.35.251:8080/health
curl -s http://54.227.35.251:8080/inspect/mild_blur?seed=1000
curl -s http://54.227.35.251:8080/inspect/heavy_blur?seed=1000
curl -s http://54.227.35.251:8080/inspect/dark?seed=1000
curl -s http://54.227.35.251:8080/inspect/glare?seed=1000
```

`/health` returned OpenCV `5.0.0`. Seed 1000 on that host: clean accepted, mild blur sharpened then accepted, heavy blur sharpened then stopped, dark rescaled then accepted, glare stopped on the first measurement. A POST of the glare fixture to `/inspect` also stopped.

`evaluate.py` writes `results/eval.json`. The blur cutoff was chosen on the 10,000 seed series. The scored rows use the 80,000 seed series from the same drawing function.

## AWS

Account `943939515056`, region `us-east-1`, one `t3.micro` (`i-0669d7039cd2ccb83`, security group `sg-0c38daa25303ad4d2`). The instance reads the code from `s3://spot-error-943939515056/app/` and listens on port 8080. This is not a COOL or Graviton deployment.

Leave the instance up while judges may open the URL. When the demo is over:

```bash
aws ec2 terminate-instances --region us-east-1 --instance-ids i-0669d7039cd2ccb83
```

## License

Copyright © 2026 Joseph C. Hoyt. All rights reserved. See `LICENSE`.

Public availability is not an open-source grant. The OpenCV and AWS contest license covers Devpost Submitted Materials only: the report, the diagram, the pasted text, and the video, if those are uploaded. It does not cover this source unless the source itself is uploaded into the submission.
