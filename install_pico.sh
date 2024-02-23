#!/bin/sh

# Install the files on a pico
if [ -z "$1" ]
  then
    echo "/dev/ttyACMx parameter missing!"
                exit 0
fi

CUR_DIR=`pwd`
while :
do

clear
echo "Wait for Pico on $1..."
while [ ! -f /media/domeu/RPI-RP2/INFO_UF2.TXT ]; do sleep 1; done
echo "Flashing MicroPython..."
cp /home/domeu/Téléchargements/upy-os/rp2-pico-20230426-v1.20.0.uf2 /media/domeu/RPI-RP2/
echo "Wait Pico reboot on $1..."
while ! (ls $1 2>/dev/null) do sleep 1; done;

# Install the files on a pico

mpremote connect $1 fs mkdir lib
echo "Installing Zumo Robot on Pico @ $1"
for LIB_FILE in $(ls lib/*.py)
do
		mpremote connect $1 fs cp $LIB_FILE :$LIB_FILE
done

mpremote connect $1 fs cp examples/main.py :main.py

for NAME in line_follower.py test_zumoshield.py test_readline2.py test_play.py test_compass.py
do
		mpremote connect $1 fs cp examples/$NAME :$NAME
done

# Test the board
mpremote connect $1 run blink.py

echo " "
echo "Done!"
done

