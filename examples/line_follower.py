"""
line_follower.py - easy linefollower Example for Pyboard & Raspberry-Pi Pico

* Author(s):  Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot
REQUIRES library qtrsensors.py in the project source
"""
#
# The MIT License (MIT)
#
# Copyright (c) 2019 Meurisse D. for MC Hobby
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN
from zumoshield import ZumoShield
from machine import WDT
from micropython import mem_info
import time, gc

z = ZumoShield()

MAX_SPEED = 100
last_error = 0
count = 0

def clamp( val, _min, _max ):
    return max(min(_max, val), _min)

print( "Press Button to start calibration" )
z.buzzer.play(">g8>>c8")
z.button.waitForButton()
# time.sleep(1)
# z.ir_calibration( motors=True )
# z.buzzer.play(">g8>>c8")

# Reload calibration data
z.ir.calibrationOn.load_json( '{"maximum": [2000, 1775, 1475, 1172, 1500, 2000], "minimum": [303, 303, 303, 303, 303, 304], "initialized": true}' )
z.ir.calibrationOff.load_json( '{"maximum": null, "minimum": null, "initialized": false}' )


try:
	wdt = WDT( timeout = 300 ) # 300ms before reset
	while(True):
	    wdt.feed()
	    position = z.ir.readLineBlack()

	    error = position -2500
	    speed_diff = (error/4) + (6*(error-last_error))
	    last_error = error

	    m1Speed = MAX_SPEED+speed_diff
	    m2Speed = MAX_SPEED-speed_diff
	    m1Speed = clamp( m1Speed, 0, MAX_SPEED )
	    m2Speed = clamp( m2Speed, 0, MAX_SPEED )

	    z.motors.setSpeeds(m1Speed,m2Speed)

	    #count += 1
	    if count%10 == 0 :
	        print("%i : position %i" % (count,position) )
	        print( mem_info() )
        gc.collect()
finally:
	z.motors.stop()
