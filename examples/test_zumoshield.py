"""
test_zumoshield.py - Test the basic features of the shield.

* Author(s):  Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot
REQUIRES library zumoshield.py in the project source
"""

from zumoshield import ZumoShield
from machine import Pin
import time

z = ZumoShield() # will stop the motors

print("Blip")
z.buzzer.play(">g32>>c32")

print( "Blink Zumo onboard LED" )
for i in range( 5 ):
	z.led.on()
	time.sleep_ms(200)
	z.led.off()
	time.sleep_ms(200)

# Activation/deactivation of IR is not visible (not in visible light)
#print( "Blink IRLED" )
#for i in range( 5 ):
#	z.ir.emittersOn()
#	time.sleep_ms(200)
#	z.ir.emittersOff()
#	time.sleep_ms(200)

print( "Move Forward" )
# Speed from -400 to +400
z.motors.setSpeeds( 200, 200 )
time.sleep(2)
print( "Stop" )
z.motors.stop()
z.buzzer.play(">g32>>c32")
time.sleep(2)
print( "Move backward")
z.motors.setSpeeds( -200, -200 )
time.sleep(2)
print( "Stop" )
z.motors.stop()
z.buzzer.play(">g32>>c32")
time.sleep(2)
print( "Car turning right" )
z.motors.setSpeeds( 400, 100 )
time.sleep(2)
print( "Car turning Left" )
z.motors.setSpeeds( 100, 400 )
time.sleep(2)
print( "Stop" )
z.motors.stop()
z.buzzer.play(">g32>>c32")
print( "Inplace Rotate Right" )
z.motors.setSpeeds( 200, -200 )
time.sleep(2)
print( "Inplace Rotate Left" )
z.motors.setSpeeds( -200, 200 )
time.sleep(2)
print( "Stop" )
z.motors.stop()
z.buzzer.play(">g32>>c32")

print( "Press the Zumo User button" )
z.button.waitForButton()
z.buzzer.play("l16 cdegreg4")
