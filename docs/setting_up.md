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
!!! tip "Using a keys file"
    If you're unable to save your OpenAI API key as a permanent environment variable, you can add it to 
    a keys file. See [Keys file](install.md#keys-file) on _Installing Dependencies_.


## Google Cloud
Google Text-to-Speech is used to narrate your tutor, and 
Google Translate is used to translate your tutor's messages to your own language.

### 1. Setting up a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/) 
2. Click on the project drop-down and then click on the "New Project" button 
3. In the "New Project" dialog, enter a name for your project
4. Click on the "Create" button to create the project

!!! abstract "Google Cloud project ID"
    The SDK installation process (see below) will require your project ID, and not the name you gave it.
    You can find your project ID on your [Google Cloud Dashboard](https://console.cloud.google.com/home/dashboard).
    Choose your project from the dropdown at the top of the screen, and you'll see your project ID under _Project Info_.

### 2. Setting up Google Cloud SDK
Download the [Google Cloud SDK client](https://cloud.google.com/sdk/docs/install-sdk). 
Follow the installation instructions for your operating system.

### 3. Enable APIs

!!! info "Check your Google Cloud project"
    When accessing the links below, make sure the project you created is the one appearing on the dropdown box at the top

1. Enable [Google Translate API](https://console.cloud.google.com/marketplace/product/google/translate.googleapis.com) for your project
2. Enable [Google Text-to-Speech API](https://console.cloud.google.com/marketplace/product/google/texttospeech.googleapis.com) for your project

