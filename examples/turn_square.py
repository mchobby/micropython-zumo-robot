""" turn_square.py - Porting the Arduino example TurnWithCompass

This example uses the Zumo Shield's onboard magnetometer to help the Zumo make
precise 90-degree turns and drive in squares. It uses ZumoMotors, Pushbutton
and ZumoIMU.

This program first calibrates the compass to account for offsets in its output.
Calibration is accomplished in setup().

In main loop(), The driving angle then changes its offset by 90 degrees from
the heading every second. Essentially, this navigates the Zumo to drive in
square patterns.

It is important to note that stray magnetic fields from electric current (including
from the Zumo's own motors) and the environment
* (for example, steel rebar in a concrete floor) might adversely
* affect readings from the compass and make them less reliable.

See project source @ https://github.com/mchobby/micropython-zumo-robot

23 jul 2021 - domeu - initial writing
07 apr 2023 - domeu - Using zumoimu.compass class
"""
from zumoshield import ZumoShield
from zumoimu import ZumoIMU, Compass
from micropython import const
import time
import math

z = ZumoShield() # Will stop motors
imu = ZumoIMU( z.i2c )

SPEED           = const( 200 ) # Maximum motor speed when going straight; variable speed when turning
TURN_BASE_SPEED = const(  80 ) # Base speed when turning (added to variable speed)
CALIBRATE_SPEED = const( 120 ) # Speed while calibrating the compass (magnetic field)


# -------- Compas Heading Toolbox --------
compass = Compass( imu )


# -------- Start Script --------
print( "Press the button to calibrate" )
z.play_blip()
z.button.waitForButton()

print("starting calibration");
z.motors.setSpeeds( CALIBRATE_SPEED,-1*CALIBRATE_SPEED )
compass.calibrate()
z.motors.stop()

print("min.x = %6i  :  max.x = %6i" % (compass.min.x, compass.max.x) )
print("min.y = %6i  :  max.y = %6i" % (compass.min.y, compass.max.y) )

print( "Press the button to START" )
z.play_blip()
z.button.waitForButton()

# -------- Main Loop --------
heading = 0.0
relative_heading = 0.0
speed = 0
target_heading = None

while True:
	if target_heading == None: # Mimic Static behavior
		target_heading = compass.average_heading() # get current raw heading

	# Heading is given in degrees away from the magnetic vector, increasing clockwise
	heading = compass.average_heading()

	# This gives us the relative heading with respect to the target angle
	rel_heading = compass.relative_heading(heading, target_heading)

	print("[Degrees] Target: %4i  ,Actual: %4i  ,Diff: %4i" % (target_heading, heading, rel_heading) )

	# If the Zumo has turned to the direction it wants to be pointing, go straight and then do another turn
	if abs(rel_heading) < Compass.DEVIATION_THRESHOLD :
		z.motors.setSpeeds(SPEED, SPEED)
		print("   Go Straight")

		time.sleep(1)

		# Turn off motors and wait a short time to reduce interference from motors
		z.motors.stop()
		time.sleep_ms(100)

		# Turn 90 degrees relative to the direction we are pointing.
		# This will help account for variable magnetic field, as opposed
		# to using fixed increments of 90 degrees from the initial
		# heading (which might have been measured in a different magnetic
		# field than the one the Zumo is experiencing now).
		# Note: fmod() is floating point modulo
		target_heading = compass.average_heading() + 90 % 360
	else:
		# To avoid overshooting, the closer the Zumo gets to the target
		# heading, the slower it should turn. Set the motor speeds to a
		# minimum base amount plus an additional variable amount based
		# on the heading difference.
		speed = int(SPEED*rel_heading/180)
		if speed < 0:
			speed -= TURN_BASE_SPEED
		else:
			speed += TURN_BASE_SPEED

		z.motors.setSpeeds(speed, -speed)

		print("   Turning")
