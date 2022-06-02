"""
test_qtrrc_readline.py - read the position of a black line (19mm) of QTR Sensor on Zumo Robot

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
#
# The setup phase of this example calibrates the sensors for ten seconds and
# turns on the Pico's LED (GPIO 25) while calibration is going  on.
# During this phase, you should expose each reflectance sensor to the
# lightest and darkest readings they will encounter. For example, if you are
# making a line follower, you should slide the sensors across the line during
# the calibration phase so that each sensor can get a reading of how dark the
# line is and how light the ground is.  Improper calibration will result in
# poor readings.
#
# The main loop of the example reads the calibrated sensor values and uses
# them to estimate the position of a line. You can test this by taping a piece
# of 19mm black electrical tape to a piece of white paper and sliding the
# sensor across it. It prints the sensor values to the serial monitor as
# numbers from 0 (maximum reflectance) to 1000 (minimum reflectance) followed
# by the estimated location of the line as a number from 0 to 5000. 1000 means
# the line is directly under sensor 1, 2000 means directly under sensor 2,
# etc. 0 means the line is directly under sensor 0 or was last seen by sensor
# 0 before being lost. 5000 means the line is directly under sensor 5 or was
# last seen by sensor 5 before being lost.

from qtrsensors import QTRSensors
from machine import Pin
import time

pin_numbers = (14,17,10,19,18,13)
pin_emitter = Pin( 16, Pin.OUT )
sv = [0]*len(pin_numbers) # sensor values

qtr = QTRSensors( [Pin(nr,Pin.OUT) for nr in pin_numbers], pin_emitter )
pin_emitter.value( 1 ) # Activate emitters

time.sleep_ms( 500 )

print( "=== Calibrating ===")
led = Pin( 25, Pin.OUT, value=1 )
# 2.5 ms RC read timeout (default) * 10 reads per calibrate() call = ~25 ms per
# calibrate() call.  Call calibrate() 400 times to make calibration take about 10 seconds.
for i in range( 400 ):
	qtr.calibrate()
led.value( 0 ) # turn off LED to indicate we are through with calibration

print( "Calibration minimum (when emitter is on)" )
values = tuple( [value for value in qtr.calibrationOn.minimum] )
print( '%4i  %4i  %4i  %4i  %4i  %4i ' % values )

print( "Calibration maximum (when emitter is on)" )
values = tuple( [value for value in qtr.calibrationOn.maximum] )
print( '%4i  %4i  %4i  %4i  %4i  %4i ' % values )

print("")
print("")
time.sleep(1)
print( "=== Reading ===")
while True:
	qtr.read( sv )
	print( '%4i  %4i  %4i  %4i  %4i  %4i ' % (sv[0],sv[1],sv[2],sv[3],sv[4],sv[5]) )
	time.sleep_ms(250)
