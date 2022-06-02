"""
test_qtrrc_rawvalues.py - read the raw values of QTR Sensor on Zumo Robot

* Author(s):  Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot
REQUIRES library zumoshield.py in the project source
"""

# This example is designed for use with six RC QTR sensors. These
# reflectance sensors should be connected to digital pins 14,17,10,19,18,13
# as defined on the Pico-Zumo adapter.
# sensors' emitter control pin (CTRL or LEDON) can optionally be connected to
# digital pin 16, or you can leave it disconnected and remove the call to setEmitterPin()
#
# The main loop of the example reads the raw sensor values (uncalibrated). You
# can test this by taping a piece of 19mm black electrical tape to a piece of
# white paper and sliding the sensor across it. It prints the sensor values to
# the REPL session as numbers from 0 (maximum reflectance) to 2500 (minimum
# reflectance; this is the default RC timeout, which can be changed with setTimeout()).

from qtrsensors import QTRSensors
from machine import Pin
import time

pin_numbers = (14,17,10,19,18,13)
pin_emitter = Pin( 16, Pin.OUT )
sv = [0]*len(pin_numbers) # sensor values

qtr = QTRSensors( [Pin(nr,Pin.OUT) for nr in pin_numbers], pin_emitter )
pin_emitter.value( 1 ) # Activate emitters

while True:
	qtr.read( sv )
	print( '%4i  %4i  %4i  %4i  %4i  %4i ' % (sv[0],sv[1],sv[2],sv[3],sv[4],sv[5]) )
	time.sleep_ms(250)
