"""
zumoshield.py - Pololu's Zumo Robot Shield library supporting the MCUs:
    * MicroPython Pyboard Original.
	* Raspberry-Pi Pico

* Author(s):    Braccio M.  from MCHobby (shop.mchobby.be).
                Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot

See example line_follower.py in the project source
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

__version__ = "0.0.3"
__repo__ = "https://github.com/mchobby/pyboard-driver.git"

# Identify the plateform
import os
is_pico = os.uname().sysname=='rp2' # Otherwise, it is Pypboad
is_pico_w = is_pico and ( 'Pico W' in os.uname().machine )


from machine import Pin, I2C
if is_pico:
	from machine import PWM
else:
	from pyb import Timer
from qtrsensors import QTRSensors
from pushbutton import Pushbutton
from zumobuzzer import PololuBuzzer
import time

if is_pico:
    BUTTON_PIN = 20
    LED_PIN = 21

    ZUMO_SENSOR_ARRAY_DEFAULT_EMITTER_PIN = 16
    PWM_L=3
    PWM_R=2
    DIR_L=11
    DIR_R=12
    REFLECT_PIN1 = 14
    REFLECT_PIN2 = 17
    REFLECT_PIN3 = 10
    REFLECT_PIN4 = 19
    REFLECT_PIN5 = 18
    REFLECT_PIN6 = 13
else:
    BUTTON_PIN = "Y7"
    LED_PIN = "Y6"

    ZUMO_SENSOR_ARRAY_DEFAULT_EMITTER_PIN = "X7"
    PWM_L="X8"
    PWM_R="X10"
    DIR_L="X9"
    DIR_R="Y5"

    REFLECT_PIN1 = "X2"
    REFLECT_PIN2 = "X22"
    REFLECT_PIN3 = "Y8"
    REFLECT_PIN4 = "X19"
    REFLECT_PIN5 = "X21"
    REFLECT_PIN6 = "X3"

class ZumoMotor( object ):

    def __init__(self,use_20khz_pwm=False):
        self.dir_l=Pin(DIR_L,Pin.OUT)
        self.dir_r=Pin(DIR_R,Pin.OUT)
        self.pwm_l=Pin(PWM_L,Pin.OUT)
        self.pwm_r=Pin(PWM_R,Pin.OUT)

        if is_pico:
            self.ch_r = PWM( self.pwm_r )
            self.ch_r.freq( 1000 if not(use_20khz_pwm) else 20000 )
            self.ch_l = PWM( self.pwm_l )
            self.ch_r.freq( 1000 if not(use_20khz_pwm) else 20000 )
        else:
            self.tim_r=Timer(4,freq=1000 if not(use_20khz_pwm) else 20000)
            self.ch_r=self.tim_r.channel(2,Timer.PWM,pin=self.pwm_r)
            self.tim_l=Timer(14,freq=500 if not(use_20khz_pwm) else 20000)
            self.ch_l=self.tim_l.channel(1,Timer.PWM,pin=self.pwm_l)

        self.flipLeft = False
        self.flipRight = False

        initialized = True # This class is always initialised and doens't need to initialised before
                           # every change of speed

    def flipLeftMotor(self,flip):
        self.flipleft = flip # True/False

    def flipRightMotor(self,flip):
        self.flipRight = flip

    def setLeftSpeed(self,speed):
        reverse=False
        if (speed<0):                                   #if speed is negatif we make tha value positif again
            speed = -speed                              #but put the reverse value to 1 so we know we need to go backwars
            reverse = True
        if(speed > 400):                                #speed can be maximum 400
            speed = 400

        # value goes from 0-400 but in python we need % for PWM Pyboard.
        #We divide by 4 to have a value that goes from 0-100
        if is_pico:
            self.ch_l.duty_u16( int((65535/100)*(speed/4)) )
        else:
            self.ch_l.pulse_width_percent(int(speed/4))
        if (reverse ^ self.flipLeft):
            self.dir_l.value(1)
        else:
            self.dir_l.value(0)

    def setRightSpeed(self,speed):
        reverse=False
        if (speed<0):
            speed = -speed
            reverse = True
        if(speed > 400):
            speed = 400

        if is_pico:
            self.ch_r.duty_u16( int((65535/100)*(speed/4)) )
        else:
            self.ch_r.pulse_width_percent(int(speed/4))
        if (reverse ^ self.flipRight):
            self.dir_r.value(1)
        else:
            self.dir_r.value(0)

    def setSpeeds(self,leftSpeed,rightSpeed):
        self.setLeftSpeed(leftSpeed)
        self.setRightSpeed(rightSpeed)

    def stop( self ):
        self.setSpeeds(0, 0)


class ZumoReflectanceSensorArray( QTRSensors ):
	def __init__(self):
		arr = [ Pin( REFLECT_PIN1, Pin.IN ), Pin( REFLECT_PIN2, Pin.IN ), Pin( REFLECT_PIN3, Pin.IN ),
				Pin( REFLECT_PIN4, Pin.IN ), Pin( REFLECT_PIN5, Pin.IN ), Pin( REFLECT_PIN6, Pin.IN ) ]
		super().__init__( arr, Pin(ZUMO_SENSOR_ARRAY_DEFAULT_EMITTER_PIN ,Pin.OUT), timeout=2000)


class ZumoShield():
	""" Create all in one class to control the Zumo """
	def __init__( self ):
		self.motors = ZumoMotor()
		self.ir = ZumoReflectanceSensorArray()
		self.led = Pin( LED_PIN, Pin.OUT )
		self.button = Pushbutton( BUTTON_PIN )
		self.buzzer = PololuBuzzer()
		self.__i2c = None

	def ir_calibration( self ):
		""" Place the Zumo over a line before running this, it will control
		   the motor to calibrate the IR sensors """
		for i in range(80):
			if(((i>10) and (i<=30)) or ((i>50) and (i <= 70))):  #entre 10 et 30 il tourne dans un sens entre 50 et 70 il tourne dans l'autre sens
				self.motors.setSpeeds(-100,100)
			else:
				self.motors.setSpeeds(100,-100)

			self.ir.calibrate()
			time.sleep(0.02)
		self.motors.stop()

	def play_2tones( self ):
		self.buzzer.play(">g8>>c8")

	def play_blip( self ):
		self.buzzer.play(">g32>>c32")

	def play_done( self ):
		self.buzzer.play("l16 cdegreg4")

	@property
	def mcu_led( self ):
		""" Microcontroler onboard LED """
		if is_pico:
			if is_pico_w:
				return Pin( 'LED' )
			else:
				return Pin( 25, Pin.OUT )
		else:
			from pyb import LED
			return LED(1)

	@property
	def i2c( self ):
		""" return reference to I2C bus used on Pico Robot """
		if self.__i2c == None:
			if is_pico:
				self.__i2c = I2C(0)
			else:
				self.__i2c = I2C(2)
		return self.__i2c
