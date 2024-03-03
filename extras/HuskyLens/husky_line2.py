"""
husky_line2.py - Line follower with AI camera & Raspberry-Pi Pico

   >>> This version is for the HuskyLens having tilt angle from Horiz. <<<

* Author(s):  Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot
REQUIRES library husky.py in the project source
"""
from zumoshield import ZumoShield
from husky import HuskyLens, Point
from math import tan, radians
import time

z = ZumoShield()
hl = HuskyLens( z.i2c )

# default speed, correction is applied to
DEFAULT_SPEED = 100
DYN_SPEED_RATIO = DEFAULT_SPEED//10
ERROR_RATIO = 0.4 # Reducing error by proportionnel ratio

# horiz. view on top is wider than bottom horiz. view
# the distorsion angle apply a correction factor on X coordonnates
DISTORTION_ANGLE = 15.376 # for 30 deg camera positionning from horz.
DISTORTION_RAD   = radians( DISTORTION_ANGLE )

# arrow with corrected position with distortion
class CorrectedArrow:
	def __init__( self ):
		self.origin = Point()
		self.target = Point()

def flatten( point ):
	""" Flatten the picture on the HuskyLens screen by applying distortion angle """
	# multiplier for the distorsion correction (-1 to substract, +1 to append)
	mult = -1 if point.x < 160 else 1 # -1 if pixel is below the half of screen
	corr_x = point.x + mult * (240-point.y) * tan( DISTORTION_RAD )
	corr_y = point.y
	return (corr_x,corr_y)


corr_arrow = CorrectedArrow()

def clamp( val, _min, _max ):
	return max(min(_max, val), _min)

print( "Press Button to start" )
z.buzzer.play(">g8>>c8")
z.button.waitForButton()
time.sleep(1)

dyn_speed = DEFAULT_SPEED
retries = 0
try:
	while(True):
		if z.button.isPressed():
			raise Exception( "User abort")
		# Querying arrow
		lst = hl.get_arrows( learned=True )
		if not(lst):
			retries+=1
			if retries > 20:
				z.motors.stop()
			continue

		arrow = lst[0] # We have an arrow
		#print( "Origin is %i,%i, Target is %i,%i" % (arrow.origin.x, arrow.origin.y, arrow.target.x, arrow.target.y) )

		# Arrow must start on the third bottom part
		if arrow.origin.y < 160:
			retries+=1
			if retries > 20:
				z.motors.stop()
			continue

		# We have arrow on the screen (starting from bottom)
		retries = 0

		# Correct the field of view distortion
		corr_arrow.target.set( flatten(arrow.target) )
		if arrow.origin.y < 230:
			corr_arrow.origin.set( flatten(arrow.origin) )
		else:
			corr_arrow.origin.set( arrow.origin )

		error = (corr_arrow.target.x-160) - (160-corr_arrow.origin.x)
		# error is in the range of -300 to +300
		speed_diff = int(error * ERROR_RATIO)

		# Dynamic Speed (reduce general speed with turning)
		dyn_speed = DEFAULT_SPEED - clamp( abs(corr_arrow.target.x-corr_arrow.origin.x)//20, 0, 3 )*DYN_SPEED_RATIO

		m1Speed = dyn_speed+speed_diff
		m2Speed = dyn_speed-speed_diff
		m1Speed = clamp( m1Speed, 0, 400 )
		m2Speed = clamp( m2Speed, 0, 400 )

		z.motors.setSpeeds(m1Speed,m2Speed)

		#print( "count = %1i | target.x = %03i | target.y = %03i" % (len(lst), arrow.target.x, arrow.target.y ) )
		print( "m1Speed = %03i | m2Speed = %03i | error = %03i | target.x = %i" % (m1Speed, m2Speed, error, arrow.target.x ))
finally:
	z.motors.stop()
	z.play_2tones()
