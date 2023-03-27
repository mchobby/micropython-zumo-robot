""" test_compass.py - calibrate the compass THEN show current heading value

See project source @ https://github.com/mchobby/micropython-zumo-robot

17 march 2022 - domeu - initial writing
"""

from zumoshield import *
from zumoimu import *
import time

SPEED = 100

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

while True:
	heading = compass.averageHeading()
	print( 'Heading %s degrees' % heading )
	time.sleep( 0.5 )
