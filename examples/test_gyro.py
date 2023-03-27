""" test_compass.py - calibrate the compass THEN show current heading value

See project source @ https://github.com/mchobby/micropython-zumo-robot

17 march 2022 - domeu - initial writing
"""

from zumoshield import *
from zumoimu import *
import time


z = ZumoShield()
imu = ZumoIMU( z.i2c )

print( "Gyroscope rotation reading" )
while True:
	imu.read_gyro()
	print( "x = %5i, y = %5i, z = %5i" % (imu.g.x, imu.g.y, imu.g.z) )
	time.sleep( 0.1 )
