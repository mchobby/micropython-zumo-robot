""" test_itoz.py - used to calibrate the INCHES_TO_ZUNITS value for maze_solver

   For Pololu Zumo Robot v1.3


  |
  |
  +---  <-- the crossroad
  |
_____
*|Z|*   <-- the Zumo
*| |*


 The Zumo first calibrates the sensors to account for differences of the black
 line on white background Calibration is accomplished.

 The Zumo will wait the user button to be pressed
    THEN it drive until the crossroad
	AND stop there.

The Zumo will wait again for the user button to be pressed
	THEN it calculates the overshoot values
	AND drive the motors to reach the overshoot distance
	AND FINALLY stop there.

The operator should:
  1) Ensure that LINE_THICKNESS fits your real labyrinth design
  2) Check that overshoot is just enough to make a proper rotation over the CrossRoad
  3) Adjust the INCHES_TO_ZUNITS (by multiple of 1000 units) to increase/decrease

02 june 2023 - domeu - initial writing
"""
from zumoshield import ZumoShield
from zumoimu import *
import time

# SENSOR_THRESHOLD is a value to compare reflectance sensor
# readings to to decide if the sensor is over a black line
SENSOR_THRESHOLD = 300

# above_line is a helper macro that takes returns
# 1 if the sensor is over the line and 0 if otherwise
def above_line(sensor):
	return sensor > SENSOR_THRESHOLD

# Motor speed when turning. TURN_SPEED should always
# have a positive value, otherwise the Zumo will turn
# in the wrong direction.
TURN_SPEED = 100

# Motor speed when driving straight. SPEED should always
# have a positive value, otherwise the Zumo will travel in the
# wrong direction.
SPEED = 200

# Thickness of your line in inches
LINE_THICKNESS = 0.78

# When the motor speed of the zumo is set by  motors.setSpeeds(200,200),
# 200 is in ZUNITs/Second. A ZUNIT is a fictitious measurement of distance
# and only helps to approximate how far the Zumo has traveled. Experimentally
# it was observed that for every inch, there were approximately 17142 ZUNITs.
# This value will differ depending on setup/battery life and may be adjusted
# accordingly. This value  was found using a 75:1 HP Motors with batteries partially discharged.
INCHES_TO_ZUNITS = 41000.0 # 17142.0

# When the Zumo reaches the end of a segment it needs
# to find out three things: if it has reached the finish line,
# if there is a straight segment ahead of it, and which
# segment to take. OVERSHOOT tells the Zumo how far it needs
# to overshoot the segment to find out any of these things.
def overshoot( line_thickness ):
	return int((INCHES_TO_ZUNITS * (line_thickness)) / SPEED)


def turn( z, dir ):
	""" Turns according to the parameter dir, which should be
		'L' (left), 'R' (right), 'S' (straight), or 'B' (back). """

	# count and last_status help keep track of how much further
	# the Zumo needs to turn.
	count = 0
	last_status = 0

	# dir tests for which direction to turn
	if dir in ('L','B'):
		# Since we're using the sensors to coordinate turns instead of timing them,
		# we can treat a left turn the same as a direction reversal: they differ only
		# in whether the zumo will turn 90 degrees or 180 degrees before seeing the
		# line under the sensor. If 'B' is passed to the turn function when there is a
		# left turn available, then the Zumo will turn onto the left segment.

		#Turn left.
		z.motors.setSpeeds(-TURN_SPEED, TURN_SPEED);

		# This while loop monitors line position until the turn is complete.
		while( count < 2 ):
			z.ir.readLineBlack()
			# Increment count whenever the state of the sensor changes
			# (white->black and black->white) since the sensor should
			# pass over 1 line while the robot is turning, the final
			# count should be 2
			count += above_line(z.ir.values[1]) ^ last_status
			last_status = above_line(z.ir.values[1])
	elif dir == 'R':
		# Turn right.
		z.motors.setSpeeds(TURN_SPEED, -TURN_SPEED)

		# This while loop monitors line position until the turn is complete.
		while( count < 2 ):
			z.ir.readLineBlack(); #was readLine()
			count += above_line(z.ir.values[4]) ^ last_status
			last_status = above_line(z.ir.values[4])
	elif dir == 'S':
		# Don't do anything!
		pass

def follow_segment( z ):
	# The maze is broken down into segments. Once the Zumo decides
	# which segment to turn on, it will navigate until it finds another
	# intersection. followSegment() will then return after the
	# intersection is found.

	position = None
	#unsigned int sensors[6];
	offset_from_center = None
	power_difference = None

	while True:
		# Get the position of the line.
		position = z.ir.readLineBlack()

		# The offset_from_center should be 0 when we are on the line.
		offset_from_center = int(position - 2500)

		# Compute the difference between the two motor power settings,
		# m1 - m2.  If this is a positive number the robot will turn
		# to the left.  If it is a negative number, the robot will
		# turn to the right, and the magnitude of the number determines
		# the sharpness of the turn.
		power_difference = offset_from_center / 3

		# Compute the actual motor settings.  We never set either motor
		# to a negative value.
		if power_difference > SPEED:
			power_difference = SPEED
		if power_difference < -SPEED:
			power_difference = -SPEED

		if power_difference < 0 :
			z.motors.setSpeeds(SPEED + power_difference, SPEED)
		else:
			z.motors.setSpeeds(SPEED, SPEED - power_difference)

		# We use the inner four sensors (1, 2, 3, and 4) for
		# determining whether there is a line straight ahead, and the
		# sensors 0 and 5 for detecting lines going to the left and
		# right.

		if all( not(above_line(sensor)) for sensor in z.ir.values ):
			# There is no line visible ahead, and we didn't see any
			# intersection.  Must be a dead end.
			return
		elif above_line(z.ir.values[0]) or above_line(z.ir.values[5]):
		 	# Found an intersection.
			return


def go_to_finish_line( z ):
	follow_segment( z )
	z.motors.stop()

	print( 'will overshoot' )
	z.play_blip()
	z.button.waitForButton()
	# Drive through the intersection.
	z.motors.setSpeeds(SPEED, SPEED)
	time.sleep_ms( overshoot(LINE_THICKNESS) )
	z.motors.stop()

	# Debugging purpose
	print( 'will turn R' )
	z.play_blip()
	z.button.waitForButton()

	# Make a turn according to the instruction stored in path[i].
	turn( z, 'R' )
	z.motors.stop()

	# Follow the last segment up to the finish.
	#self.follow_segment()
	return


# --- Setup --------------------------------------------------------------------
z = ZumoShield() # Desendant of ZumoShield

z.play_blip()
z.ir.emittersOn()
time.sleep_ms( 500 )
z.led.on()


# do calibration OR reload existing values
do_calibrate = True
if do_calibrate:
	z.button.waitForButton()
	# Calibrate the Zumo by sweeping it from left to right
	# note: Replace the original Pololu code with a predefined one
	z.ir_calibration()
	# Turn left.
	z.turn('L')
	z.motors.stop()
	# Sound off buzzer to denote Zumo is finished calibrating
	z.buzzer.play("L16 cdegreg4")
else:
	# Setup with your predefined calibration data
	z.ir.calibrationOn.load_json( '{"maximum": [2000, 2000, 1669, 1787, 2000, 2000], "minimum": [365, 365, 262, 260, 371, 371], "initialized": true}' )

# Turn off LED to indicate we are through with calibration
z.led.off()
z.buzzer.play(">>a32")

# The maze has been solved. When the user places the Zumo at the starting line
# and pushes the Zumo button, the Zumo knows where the finish line is and
# will automatically navigate.
z.button.waitForButton()
go_to_finish_line( z )
z.buzzer.play(">>a32")
