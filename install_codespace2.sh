#!/bin/bash
./google-cloud-sdk/bin/gcloud init
gcloud auth application-default login
echo ""
echo "Codespace setup complete! Don't forget to add your OpenAI API key as a secret."