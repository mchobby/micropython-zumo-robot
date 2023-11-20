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

from zumoshield import *
import time

z = ZumoShield()
z.ir.emittersOn()

while True:
	z.ir.read()
	print( '%4i  %4i  %4i  %4i  %4i  %4i ' % (z.ir.values[0],z.ir.values[1],z.ir.values[2],z.ir.values[3],z.ir.values[4],z.ir.values[5]) )
	time.sleep_ms(250)
