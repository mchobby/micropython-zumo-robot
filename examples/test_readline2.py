""" test_ readline2.py - enhanced line reading example involving button & buzzer libraries.

	calibrate the line sensor (move it over the line) then detect the position of the line.

See project source @ https://github.com/mchobby/micropython-zumo-robot

18 may 2022 - domeu - initial testing
"""
# Just stop the motors
from zumoshield import ZumoShield
import time

z = ZumoShield()

# Gives use the time to place the Zumo over a line.
print( "Place zumo over a line and press button.")
print( "   Motors will be controled for IR Sensor calibration")
z.play_blip()
z.button.waitForButton()
time.sleep(1)

# Move the Zumo over the line while calibrating (in 10 steps).
# This will helps to identifies the white/black contrast.
print( "Calibrating IR Line sensor..." )
z.ir_calibration()
z.play_blip()
print( ' ')

print( "Press button to read line sensor" )
print( "   Motors will not be controled" )
z.button.waitForButton()

# Read the line position @ max speed but will displays result ebery seconds
#
last = time.time()
while True:
	# With the Zumo blade going forward
	#   Value from 500 to 4500 : line is placed from left to right
	#   value 2500 : line centered on the zumo
	#   value 0 : line exceed on the left
	#   value 5000 : line exceed on the right
	position = z.ir.readLineBlack( )
	if (time.time() - last) > 1:
		print( 'Line position: %5i  - Sensors: %s' % (position, sensors) )
		last = time.time()
