""" test_compass2.py - calibrate the compass THEN show current heading value and relative angle to the target.
                       when pressing the user button it acquires the current value and calculate target = current angle + 90°

See project source @ https://github.com/mchobby/micropython-zumo-robot

07 april 2023 - domeu - Initial writing
"""

from zumoshield import *
from zumoimu import *
import time

SPEED = 120

z = ZumoShield()
imu = ZumoIMU( z.i2c )
compass = Compass( imu )

print("Press the button to start calibration!")
z.play_blip()
z.button.waitForButton()
print("Starting calibration...")
z.motors.setSpeeds( SPEED, -SPEED )
compass.calibrate()
z.motors.stop()
z.play_blip()
print("calibration done")
print( 'Compass min: %s ' % compass.min )
print( 'Compass max: %s ' % compass.max )
print("Press button to set target angle" )
heading = None
target  = None
while True:
	heading = compass.average_heading()
	if target == None: # initialize target
		target = heading
	# if user button pressed -> acquire target value
	if z.button.isPressed():
		target = ( heading + 90) % 360
	# Relative angle to target
	relative = compass.relative_heading( heading, target )
	print( 'Heading %3.1f | Target %3.1f | Relative %3.1f' % (heading,target,relative) )
	time.sleep( 0.5 )
