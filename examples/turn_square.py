""" turn_compass.py - Porting the Arduino example TurnWithCompass

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
"""
from zumoshield import ZumoShield
from zumoimu import ZumoIMU, Vector
from micropython import const
import time
import math

z = ZumoShield() # Will stop motors
imu = ZumoIMU( z.i2c )

SPEED           = const( 200 ) # Maximum motor speed when going straight; variable speed when turning
TURN_BASE_SPEED = const( 100 ) # Base speed when turning (added to variable speed)

CALIBRATION_SAMPLES = const( 70 ) # Number of compass readings to take when calibrating
DEVIATION_THRESHOLD = const( 5 ) # Allowed deviation (in degrees) relative to target angle that must be achieved before driving straight

m_max = Vector() # maximum magnetometer values, used for calibration
m_min = Vector() # minimum magnetometer values, used for calibration

running_min = Vector( 32767, 32767, 32767 )
running_max = Vector( -32767, -32767, -32767 )

# -------- Compas Heading Toolbox --------
imu.config_for_compass_heading()

def heading_degrees( v ):
	# Converts x and y components of a vector (v) to a heading in degrees (float).
	# This calculation assumes that the Zumo is always level.
	global m_min, m_max
	x_scaled =  2.0*(v.x - m_min.x) / (m_max.x - m_min.x) - 1.0
	y_scaled =  2.0*(v.y - m_min.y) / (m_max.y - m_min.y) - 1.0

	angle = math.atan2(y_scaled, x_scaled)*180 / math.pi
	if angle < 0:
		angle += 360
	return angle

def average_heading(imu):
	#  Average 10 vectors to get a better measurement and help smooth out
	# the motors' magnetic interference. Returns the average heading in degrees (float)
	avg = Vector( 0.0, 0.0, 0.0 )
	for i in range( 10 ):
		imu.read_mag()
		avg.x += imu.m.x
		avg.y += imu.m.y
	avg.x /= 10.0
	avg.y /= 10.0
	# avg is the average measure of the magnetic vector.
	return heading_degrees( avg )

def relative_heading_degrees( heading_from, heading_to) :
	# Yields the angle difference in degrees between two headings in headings
	rel_heading = heading_to - heading_from
	# constrain to -180 to 180 degree range
	if rel_heading > 180:
		rel_heading -= 360
	if rel_heading < -180:
		rel_heading += 360
	return rel_heading


# -------- Start Script --------
print( "Press the button to calibrate" )
z.play_blip()
z.button.waitForButton()

print("starting calibration");
z.motors.setSpeeds( SPEED, -SPEED )

for index in range( CALIBRATION_SAMPLES ):
	# Take a reading of the magnetic vector and store it in compass.m
	imu.read_mag()
	running_min.x = min(running_min.x, imu.m.x)
	running_min.y = min(running_min.y, imu.m.y)

	running_max.x = max(running_max.x, imu.m.x);
	running_max.y = max(running_max.y, imu.m.y);
	print( "  %i" % index )
	time.sleep_ms(50)

z.motors.stop()
print("min.x = %6i  :  max.x = %6i" % (running_min.x, running_max.x) )
print("min.y = %6i  :  max.y = %6i" % (running_min.y, running_max.y) )
# Store calibrated values in m_max and m_min
m_max.set( running_max.values )
m_min.set( running_min.values )

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
		target_heading = average_heading(imu) # get current raw heading

	# Heading is given in degrees away from the magnetic vector, increasing clockwise
	heading = average_heading(imu)

	# This gives us the relative heading with respect to the target angle
	rel_heading = relative_heading_degrees(heading, target_heading)

	print("[Degrees] Target: %4i  ,Actual: %4i  ,Diff: %4i" % (target_heading, heading, rel_heading) )

	# If the Zumo has turned to the direction it wants to be pointing, go straight and then do another turn
	if abs(rel_heading) < DEVIATION_THRESHOLD :
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
		target_heading = average_heading(imu) + 90 % 360
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
