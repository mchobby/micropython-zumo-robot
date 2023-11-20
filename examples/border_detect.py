"""
border_detect.py - easy sumo-robot white border detect

* Author(s):  Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot
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
from zumobuzzer import NOTE_G
import time

QTR_THRESHOLD = 1000
FORWARD_SPEED = 200
REVERSE_SPEED = -150
TURN_SPEED    = 200
REVERSE_DURATION= 400
TURN_DURATION   = 400

z=ZumoShield()

def waitForButtonAndCountDown():
    global z
    z.led.value(1)
    z.button.waitForButton()
    z.led.value(0)
    for x in range(3):
        time.sleep(1)
        z.buzzer.playNote( NOTE_G(3),200,15 )
    time.sleep(1)
    z.buzzer.playNote( NOTE_G(4),500,15 )
    time.sleep(1)

left_count = 0
right_count= 0
z.play_blip()
waitForButtonAndCountDown()

while(True):
    z.ir.read()
    if z.ir.values[0] < QTR_THRESHOLD :
        z.motors.setSpeeds( REVERSE_SPEED,REVERSE_SPEED )
        time.sleep_ms( REVERSE_DURATION )
        z.motors.setSpeeds( TURN_SPEED,-1*TURN_SPEED )
        time.sleep_ms( TURN_DURATION )
        z.motors.setSpeeds( FORWARD_SPEED,FORWARD_SPEED )
        left_count+=1

    elif z.ir.values[5] < QTR_THRESHOLD :
        if left_count>3 and right_count>3 :
            REVERSE_DURATION = 800
            TURN_DURATION    = 800
            left_count = 0
            right_count= 0
        z.motors.setSpeeds( REVERSE_SPEED,REVERSE_SPEED )
        time.sleep_ms( REVERSE_DURATION )
        z.motors.setSpeeds( -1*TURN_SPEED,TURN_SPEED )
        time.sleep_ms( TURN_DURATION )
        z.motors.setSpeeds( FORWARD_SPEED,FORWARD_SPEED )

        REVERSE_DURATION = 400
        TURN_DURATION    = 400
        right_count+=1

    else:
        z.motors.setSpeeds( FORWARD_SPEED,FORWARD_SPEED )
