# Installing Dependencies

## Installing prerequisites

=== ":simple-apple: Mac"

    ```bash
    brew install ffmpeg
    ```

=== ":simple-linux: Linux"

    ```bash
    apt-get install ffmpeg libavcodec-extra
    ```  

=== ":fontawesome-brands-windows: Windows"

    !!! bug "libav.org is down"
        It seems the Windows binaries website is down. If you find an alternative method to install Companion on Windows,
        please update on the [open issue on GitHub](https://github.com/shakedzy/companion/issues/52).

    1. Download and extract `libav` from the [Windows binaries](http://builds.libav.org/windows/).
    2. Add the `libav`'s `/bin` folder to your `PATH` envvar


## Installing environment

1. Create a new virtual environment _(optional)_

2. Clone the repository, either by downloading the files
  from GitHub or by running:
```bash
git clone https://github.com/shakedzy/companion.git
```
3. From the main `companion` directory, run:
```bash
pip install -r requirements.txt
```


## Keys file
**This is optional, and not required.**

You may add a `keys.yml` file which will hold your OpenAI API configurations and/or a Google Cloud Service Account
to be used to access these required services. It allows you to override the local
OpenAI API key or Google Cloud SDK (or when they cannot be installed).

!!! warning "Private keys"
    Your API and Service Account keys are private and shouldn't be shared, as they
    allow access your OpenAI and Google Cloud services without any password or additional logins.
    Do not save or share this file publicly online nor commit it to GitHub. This file should
    remain only on your machine.

Keys file example:
```yaml
openai:
  api_key: 'sk-...'
  base_url: '...'

google_sa:
  ...
```

#### `openai`
* `api_key`: Use this Open API key instead of the one found in your `OPENAI_API_KEY` environment variable. You can redirect to another environment variable by using the variable name with a prefix `$` prefix (i.e. `$ANOTHER_SERVICE_API_KEY`)
* `base_url`: Use this URL instead of the default one
#### `google_sa`
Insert here all your Google Service Account credentials key-values in order to authenticate with Google Cloud
using this Service Account instead of using Google Cloud SDK client. 

!!! info "Service Account roles" 
    The Service Account used for this app will require the _Service Usage Consumer_ role.
