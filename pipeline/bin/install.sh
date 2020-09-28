#!/usr/bin/env bash

# run docker and wait for ready
timeout 15 sh -c 'until docker info; do echo .; sleep 1; done' && nohup /usr/local/bin/dockerd \
  --host=unix:///var/run/docker.sock \
  --host=tcp://127.0.0.1:2375 \
  --storage-driver=overlay2 &

npm install -g aws-cdk

pip install -r requirements.txt