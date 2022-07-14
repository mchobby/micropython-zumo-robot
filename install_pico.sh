#!/bin/sh
# Install the files on a pico
if [ -z "$1" ]
  then
    echo "/dev/ttyACMx device missing!"
		exit 0
fi

mpremote connect $1 fs mkdir lib
echo "Installing Zumo Robot on Pico @ $1"
for LIB_FILE in $(ls lib/*.py)
do
		mpremote connect $1 fs cp $LIB_FILE :$LIB_FILE
done

mpremote connect $1 fs cp examples/main.py :main.py

for NAME in line_follower.py test_zumoshield.py test_readline2.py test_play.py test_mag.py
do
		mpremote connect $1 fs cp examples/$NAME :$NAME
done
echo " "
echo "Done!"
