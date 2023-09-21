#!/bin/bash
sudo apt-get update
sudo apt-get install ffmpeg libavcodec-extra
pip install -r requirements.txt
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-446.0.1-linux-x86.tar.gz
tar -xf google-cloud-cli-446.0.1-linux-x86.tar.gz
./google-cloud-sdk/install.sh
echo ""
echo "Restart your terminal and run: ./install_codespace2.sh"