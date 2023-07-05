# Installing Dependencies

### Installing prerequisites

=== "Mac"

    Run:
    ```bash
    brew install portaudio ffmpeg
    ```

=== "Linux"

    Run:
    ```bash
    apt-get install portaudio ffmpeg
    ```

### Installing environment  


1. Create a new virtual environment _(optional)_

2. Clone the repository, either by downloading the files
  from GitHub or by running:
```bash
git clone https://github.com/shakedzy/companion.git
```
3. From the main `companion` directory, run:
```bash
pip install -r requirments.txt
```


## Keys file (optional)
You may add a `keys.yml` file which will hold your OpenAI API key and/or a Google Cloud Service Account
to be used to access these required services. This is optional, and is used only when you wish to override the local
OpenAI API key or Google Cloud SDK (or when they cannot be installed).

#### openai
* `api_key`: Use this Open API key instead of the one found in your `OPENAI_API_KEY` environment variable

#### google_sa
Insert here all your Google Service Account credentials key-values in order to authenticate with Google Cloud
using this Service Account instead of using Google Cloud SDK client. Note that this Service Account
will require the "Service Usage Consumer" role.