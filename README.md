# BRBBot

## Installtion & Setup
BRBBot was built and tested using python 3.12.2.

### Ensure Python 3.12+ is installed
https://www.geeksforgeeks.org/how-to-install-python-on-windows/

### Ensure pip is installed
https://www.geeksforgeeks.org/how-to-install-pip-on-windows/

### Install Depdencies
From the root directory execute:

```
pip install -r requirements.txt
```

### Setup Configuration File
- Add twitch-dev api key and secret to the appropiate fields of config.yaml
    + Register a twitch-dev account: https://dev.twitch.tv/
    + From "You Console" register an application
    + Generate a secret from you application
- Add a stream channel name you feel comftorable typing commands in to the channels section

### Load Assets Directory
- Requires a png file using a single color and alpha channel called logo.png
- Requires .wav or .ogg sound files called bonk.wav and splat.wav
    + Multiple sound files can be loaded to cycle between sounds as long as they begin with bonk and splat.
- Requires a .wav or .ogg sound file called cheer.wav
- Expects the Consolas.ttf font to exist in the assets directory

### Verify Succesful Installtion
From the /src directory execute:

```
pything brbbot.py
```

The script must be launched from the src directory.







      (_)         | |       (_)                 
       _ _   _ ___| |_       _  __ _ _ __   ___ 
      | | | | / __| __|     | |/ _` | '_ \ / _ \
      | | |_| \__ \ |_      | | (_| | | | |  __/
      | |\__,_|___/\__|     | |\__,_|_| |_|\___|
     _/ |           ______ _/ |                 
    |__/           |______|__/
