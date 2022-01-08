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

## Speech control

* `train connect|disconnect`: Connect to the train
* `train stop|stop`: Start or stop
* `move forward|backwards`: Change direction of move
* `reverse [gently, now]`: Switch movement direction.
  * `gently` is the default.
  * `now` causes sudden change without slowing down. 
* `keep left|straight|right`: Baseline behaviour on all junctions
* `next left|straight|right`: Override baseline behaviour for next junction
* `speed one|two|three|four|five|minimum|maximum|slower|faster`: Set speed level
* `snaps ignore|follow`: Ignore or follow the default snap commands


### Programing the above commands for snaps ###

This programs a sequence of one or more colours to execute one of the above commands

    program ANY_OF_THE_ABOVE_COMMANDS when color1 [color2] [color3] [colour4]`

e.g.:

* `program train stop|stop when color_sequence`
* `program keep left|straight|right when color_sequence`
* `program next left|straight|right when color_sequence`
* ...
