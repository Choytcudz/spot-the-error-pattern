#!/bin/bash
set -euxo pipefail
exec > /var/log/user-data.log 2>&1
export AWS_DEFAULT_REGION=us-east-1
dnf install -y python3.11 python3.11-pip
mkdir -p /opt/spot
aws s3 sync s3://spot-error-943939515056/app/ /opt/spot/
python3.11 -m pip install -r /opt/spot/requirements.txt
cd /opt/spot
nohup python3.11 app.py > /var/log/spot.log 2>&1 &
