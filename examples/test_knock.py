""" test_knock.py - calibrate the accelerometer THEN detect knock on the zumo

See project source @ https://github.com/mchobby/micropython-zumo-robot

22 march 2023 - domeu - initial writing
"""

from zumoshield import *
from zumoimu import *
import time

z = ZumoShield()
imu = ZumoIMU( z.i2c )

class MeanEval:
	""" Mean & Thresold calculator """

	def __init__( self, th_x = 20, th_y = 20 ):
		# Store the last 10 readings
		# th_x, th_y: Thresold of detection in X and Y position
		self.pos = 0
		self.x_val = [0,0,0,0,0,0,0,0,0,0]
		self.y_val = [0,0,0,0,0,0,0,0,0,0]
		self.th_x = th_x
		self.th_y = th_y

	def push( self, x, y ):
		self.x_val[self.pos] = x
		self.y_val[self.pos] = y
		self.pos += 1
		if self.pos > 9:
			self.pos = 0

	def mean( self ):
		# calculate the mean X,Y position
		return ( sum(self.x_val)/10, sum(self.y_val)/10 )

	def is_knock( self, x, y ):
		# check if the values is a knocking <0,0,>0 for each axis
		x_mean, y_mean = self.mean()
		x_delta, y_delta = 0, 0
		if abs( x-x_mean )>self.th_x:
			x_delta = x - x_mean
		if abs( y-y_mean )>self.th_y:
			y_delta = y - y_mean
		return x_delta, y_delta


print( 'Don t move while calibrating!')
print("Press the button to start calibration!")
z.play_blip()
z.button.waitForButton()
print("Starting calibration...")
mean_eval = MeanEval( th_x=2000, th_y=2000 ) # With threasold
for i in range(10):
	imu.read_acc()
	mean_eval.push( imu.a.x, imu.a.y )
print("calibration done")
z.play_blip()
print(" ")


print( 'Knock it' )
while True:
	# read magnetic and accelerometer
	imu.read_acc()
	# Access the accelerometer vector

	xdelta,ydelta = mean_eval.is_knock(imu.a.x, imu.a.y)
	if (xdelta==0) & (ydelta==0): # No knocking detected
		mean_eval.push( imu.a.x, imu.a.y )
		continue

	print( '-----------------' )
	if xdelta < 0:
		print( "FRONT knock" )
	elif xdelta > 0:
		print( "BACK knock" )

	if ydelta < 0:
		print( "LEFT knock" )
	elif ydelta > 0:
		print( "RIGHT knock" )

	time.sleep( 0.100 )
