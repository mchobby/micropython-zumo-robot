""" rctank.py - control the Zumo Robot with a tank alike control

See project source @ https://github.com/mchobby/micropython-zumo-robot

09 june 2023 - domeu - initial writing
"""

from zumoshield import *
from machine import Pin, time_pulse_us
import time

ch_left  = Pin( 7, Pin.IN )
ch_right = Pin( 6, Pin.IN )

z = ZumoShield()

while True:
	us_left  = time_pulse_us( ch_left, 1 ) # pulse_level=1
	us_right = time_pulse_us( ch_right, 1 )
	print( us_left, us_right )
	time.sleep(1)
