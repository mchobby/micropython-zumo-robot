""" rcjoy.py - control the Zumo Robot with a single joystick control

See project source @ https://github.com/mchobby/micropython-zumo-robot

09 june 2023 - domeu - initial writing
"""

from zumoshield import *
from machine import Pin, time_pulse_us
import time

SPEED_CENTER_US = 1489 # ch 3
DIR_CENTER_US = 1551   # ch 1
RANGE_US = 400

ch_speed  = Pin( 7, Pin.IN ) # ch 3
ch_dir = Pin( 6, Pin.IN )    #


def map(value, istart, istop, ostart, ostop):
  return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

z = ZumoShield()
z.play_blip()
while True:
	us_speed  = time_pulse_us( ch_speed, 1 )
	us_dir = time_pulse_us( ch_dir, 1 )

	if (us_speed < 0) or (us_dir < 0):
		z.motors.stop()
		z.led.toggle()
		# no need to sleep, time_pulse_us timeout
		# will insert the required delay in the execution.
		continue

	# uSec --> -400 to +400
	speed = map( us_speed, SPEED_CENTER_US-RANGE_US, SPEED_CENTER_US+RANGE_US, +300, -300 )
	dir_diff = map( us_dir, DIR_CENTER_US+RANGE_US, DIR_CENTER_US-RANGE_US, -100, +100 )

	# print( speed, dir_diff )
	if abs(speed)<=25:
		speed = 0
	if abs(dir_diff)<=10:
		dir_diff = 0
	if speed<=-25:
		dir_diff *= -1
	elif speed==0:
		dir_diff *= 2
	speed_left = int(speed + dir_diff)
	speed_right = int(speed - dir_diff)
	if speed_left<-400:
		speed_left = -400
	if speed_left>400:
		speed_left = 400
	if speed_right<-400:
		speed_right=-400
	if speed_right>400:
		speed_right=400
	#print( us_speed," ", us_dir, " | ",  speed_left, " ", speed_right )
	z.motors.setSpeeds( speed_left, speed_right )
	time.sleep_ms(100)
