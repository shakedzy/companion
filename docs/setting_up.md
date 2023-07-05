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


## Google 
Google Text-to-Speech is used to narrate your tutor, and 
Google Translate is used to translate your tutor's messages to your own language.

### 1. Setting up a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/) 
2. Click on the project drop-down and then click on the "New Project" button 
3. In the "New Project" dialog, enter a name for your project
4. Click on the "Create" button to create the project

### 2. Setting up Google Cloud SDK
1. Download the [Google Cloud SDK client](https://cloud.google.com/sdk/docs/install-sdk). Unzip and place in your home directory
2. Run: 
```bash
~/google-cloud-sdk/install.sh`
```
3. Run:
```bash
~/google-cloud-sdk/bin/gcloud init
```
4. **Open a new terminal** and run:
```bash
gcloud auth application-default login
```

### 3. Enable APIs

!!! info "Check your Google Cloud project"
    When accessing the links below, make sure the project you created is the one appearing on the dropdown box at the top

1. Enable [Google Translate API](https://console.cloud.google.com/marketplace/product/google/translate.googleapis.com) for your project
2. Enable [Google Text-to-Speech API](https://console.cloud.google.com/marketplace/product/google/texttospeech.googleapis.com) for your project

