""" test_imu.py - Just load the library and check its initialisation

For Pololu Zumo Robot v1.3

See project source @ https://github.com/mchobby/micropython-zumo-robot

15 june 2022 - domeu - initial writing
"""
from zumoshield import ZumoShield
from zumoimu import *
import time

IMU_TYPE_LSM303DLHC = 1       # LSM303DLHC accelerometer + magnetometer
IMU_TYPE_LSM303D_L3GD20H = 2  # LSM303D accelerometer + magnetometer, L3GD20H gyro
IMU_TYPE_LSM6DS33_LIS3MDL = 3 # LSM6DS33 gyro + accelerometer, LIS3MDL magnetometer

imu_type_as_text = { IMU_TYPE_LSM303DLHC : "LSM303DLHC", IMU_TYPE_LSM303D_L3GD20H : "LSM303D_L3GD20H", IMU_TYPE_LSM6DS33_LIS3MDL : "LSM6DS33_LIS3MDL" }

z = ZumoShield() # Will stop motors
print( "Zumo I2C scan:", z.i2c.scan() )

imu = ZumoIMU( z.i2c ) # Start with auto detection
print( "IMU type: %s" % imu_type_as_text[imu.imu_type] )

while True:
	imu.read()
	print( "Acc= %6i, %6i, %6i  :  Mag= %6i, %6i, %6i  :  Gyro= %6i, %6i, %6i  " % (imu.a.values+imu.m.values+imu.g.values) )
	time.sleep( 0.5 )
