"""
husky_line.py - Line follower with AI camera & Raspberry-Pi Pico

   >>> This version is for the horizontal HuskyLens (looking downward) <<<

* Author(s):  Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot
REQUIRES library husky.py in the project source
"""
from zumoshield import ZumoShield
from husky import HuskyLens
import time

z = ZumoShield()
hl = HuskyLens( z.i2c )

# default speed, correction is applied to
DEFAULT_SPEED = 100
DYN_SPEED_RATIO = DEFAULT_SPEED//10 # 10%
ERROR_RATIO = 0.5 # Reducing error by proportionnel ratio

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

		# We have an arrow
		arrow = lst[0]

		# Arrow must start on the third bottom part
		if arrow.origin.y < 160:
			retries+=1
			if retries > 20:
				z.motors.stop()
			continue

		# We have arrow on the screen (starting from bottom)
		retries = 0

		# error is in the range of -300 to +300
		error = (arrow.target.x-160) - (160-arrow.origin.x)
		speed_diff = int(error * ERROR_RATIO)

		# Dynamic Speed (reduce general speed with turning)
		dyn_speed = DEFAULT_SPEED - clamp( abs(arrow.target.x-arrow.origin.x)//20, 0, 3 )*DYN_SPEED_RATIO

		m1Speed = dyn_speed+speed_diff
		m2Speed = dyn_speed-speed_diff
		m1Speed = clamp( m1Speed, 0, 400 )
		m2Speed = clamp( m2Speed, 0, 400 )

		z.motors.setSpeeds(m1Speed,m2Speed)
		# print( "m1Speed = %03i | m2Speed = %03i | error = %03i " % (m1Speed, m2Speed, error ))
finally:
	z.motors.stop()
	z.play_2tones()
