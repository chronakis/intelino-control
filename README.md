# intelino-apps #

A collection of small "apps" written for the intelino smart train.


## Prerequisites ##

* Python 3.9 or higher
* Python-tk for 3.9
* For the speech recognition, you may need `PyAudio` (microphone). Have look here: https://github.com/Uberi/speech_recognition#requirements
* For specific libraries
  * Google Speech to text API
    * Account (TODO: add link)
  * Rhino speech-to-intent engine
    * Console account
    * Download your own model files.

## Run/Install ##

    $ python3 -m venv .env
    $ source .env/bin/activate
    $ pip3 install < requirements.txt
    $ python3 src/main.py


