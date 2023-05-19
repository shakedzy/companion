# Setting Up Required Services

## OpenAI
The OpenAI API will be used both for the chat (using ChatGPT) and Speech-to-Text (using Whisper).

1. Create an account on [OpenAI's website](https://openai.com/)
2. Set up a [Paid Account](https://platform.openai.com/account/billing/overview)
3. Create an [API token](https://platform.openai.com/account/api-keys)
4. Save your token as an environment variable named `OPENAI_API_KEY`:
```bash
export OPENAI_API_KEY="YOUR_KEY"
```

## IBM Watson
IBM Watson will be used for Speech-to-Text.

1. Sign up for the [Text-to-Speech](https://cloud.ibm.com/catalog/services/text-to-speech) plan
2. From the [Watson Dashboard](https://cloud.ibm.com/developer/watson/dashboard), select Text-to-Speech
3. Set a new API, you'll get both an API key and a URL
4. Save the API key as an environment variable named `WATSON_API_KEY`:
```bash
export WATSON_API_KEY="YOUR_KEY"
```
5. Keep the URL, you'll need to add it to the config file later


## Google Translate
Google Translate is used to translate your tutor's messages to your own language.

### 1. Setting up a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/) 
2. Click on the project drop-down and then click on the "New Project" button 
3. In the "New Project" dialog, enter a name for your project
4. Click on the "Create" button to create the project

### 2. Setting up Google Cloud SDK
1. Download the [Google Cloud SDK client](https://cloud.google.com/sdk/docs/install-sdk). Unzip and place in your home directory.
2. Run `~/google-cloud-sdk/install.sh`
3. Run `~/google-cloud-sdk/bin/gcloud init`
4. **Open a new terminal** and run `gcloud auth application-default login`
5. Enable Translate API on [Google Cloud](https://console.cloud.google.com/apis/library/translate.googleapis.com). MAke sure the project you created is the one appearing on thee dropdown box at the top. 

