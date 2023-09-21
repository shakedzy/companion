# Use on Mobile via GitHub Codespaces

In order to use Companion on your mobile device, you can use GitHub Codespaces as your server.
For this, you'll need to have a GitHub account. It is also recommended to first install and launch Companion 
locally on your computer, to make sure all required services are configured correctly.

## Setting up your GitHub Codespace
1. Create a [new Codespace](https://github.com/codespaces/new)
   * Select `shakedzy/companion` as the repository
   * Select `main` as the branch
   * You can use the smallest machine (2 cores)
2. Got to your Codespace, and wait for it to finish initialization
3. In the terminal, run:
```bash
./install_codespace.sh
```
4. When the script ends, open a new terminal (from the menu on the left) and run:
```bash
./install_codespace2.sh
```
5. Add your `OPENAI_API_KEY` as a [secret](https://docs.github.com/en/codespaces/managing-your-codespaces/managing-secrets-for-your-codespaces#adding-a-secret). 
   Remember to name it `OPENAI_API_KEY`. This will restart your Codespace.
6. When your Codespace relaunches, run:
```bash
python companion.py
```
You can shut down your Codespace when you're done, and relaunch it when you want to use Companion again.
When you relaunch it, all you'll need to run is `python companion.py`.

!!! tip "Make Port 5000 Public"
    Connection to the service seems to work faster when port 5000 (the one used by this app)
    is made public. You'll be given the option to do so as soon as the app launches on your Codespace,
    or you can change the port visibility on the Ports tab.<br>
    Note this means that anyone with a link to your Codespace will be able to access you running app.


## Using Companion From Your Mobile
1. Once your Companion is running on your Codespace, got to the _Ports_ tab. You should see port 5000 is open.
2. Copy-paste its URL, and access it from your mobile browser.

### Mobile UI
<p align="center">
  <img src="../images/mobile.png" style="width: 75%">
</p>