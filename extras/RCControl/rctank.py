""" rctank.py - control the Zumo Robot with a tank alike control

See project source @ https://github.com/mchobby/micropython-zumo-robot

09 june 2023 - domeu - initial writing
"""

from zumoshield import *
from machine import Pin, time_pulse_us
import time

LEFT_CENTER_US = 1491
RIGHT_CENTER_US = 1484
RANGE_US = 400

ch_left  = Pin( 7, Pin.IN )
ch_right = Pin( 6, Pin.IN )


def map(value, istart, istop, ostart, ostop):
  return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

z = ZumoShield()
z.play_blip()
while True:
	us_left  = time_pulse_us( ch_left, 1 )
	us_right = time_pulse_us( ch_right, 1 )

	if (us_left < 0) or (us_right < 0):
		z.motors.stop()
		z.led.toggle()
		# no need to sleep, time_pulse_us timeout
		# will insert the required delay in the execution.
		continue

	# uSec --> -400 to +400
	speed_left = map( us_left, LEFT_CENTER_US-RANGE_US, LEFT_CENTER_US+RANGE_US, -400, +400 )
	speed_right = map( us_right, RIGHT_CENTER_US-RANGE_US, RIGHT_CENTER_US+RANGE_US, -400, +400 )
	speed_right = -1*speed_right

	if abs(speed_left)<=25:
		speed_left = 0
	if abs(speed_right)<=25:
		speed_right = 0
	z.motors.setSpeeds( speed_left, speed_right )
	time.sleep_ms(100)
