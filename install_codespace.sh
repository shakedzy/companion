#!/bin/bash
sudo apt-get update
pip install -r requirements.txt
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-446.0.1-linux-x86.tar.gz
tar -xf google-cloud-cli-446.0.1-linux-x86.tar.gz
./google-cloud-sdk/install.sh
source /home/codespace/.bashrc
./google-cloud-sdk/bin/gcloud init
gcloud auth application-default login
