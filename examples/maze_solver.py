""" maze_solver.py - Use the Zumo Reflectance Sensor Array to navigate black
   line maze with no loops.

For Pololu Zumo Robot v1.3

 The Zumo first calibrates the sensors to account for differences of the black
 line on white background Calibration is accomplished in "setup" section.

 In "loop" section, the function solve_maze() is called and navigates the Zumo
 until it finds the finish line which is defined as a large black area that
 is thick and wide enough to cover all six sensors at the same time.

 Once the Zumo reaches the finishing line, it will stop and wait for the user
 to place the Zumo back at the starting line. The Zumo can then follow the
 shortest path to the finish line.

 The macros SPEED, TURN_SPEED, above_line(), and LINE_THICKNESS might need to
 be adjusted on a case by case basis to give better line following results.

See project source @ https://github.com/mchobby/micropython-zumo-robot
Based on Pololu MazeSolver.ino @
   https://github.com/pololu/zumo-shield-arduino-library/blob/master/examples/MazeSolver/MazeSolver.ino

  july 21, 2022 - domeu - Arduino to MicroPython portage
  june 2,  2023 - domeu - Code optimisation
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
SPEED = 100

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

class MazeSolver(ZumoShield):
	def __init__(self):
		super().__init__()

		# path[] keeps a log of all the turns made since starting the maze
		self.path = list()

	@property
	def path_len( self ):
		return len( self.path )
	# --- Helper -------------------------------------------------------------------
	def turn( self, dir ):
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
			self.motors.setSpeeds(-TURN_SPEED, TURN_SPEED);

			# This while loop monitors line position until the turn is complete.
			while( count < 2 ):
				self.ir.readLineBlack()
				# Increment count whenever the state of the sensor changes
				# (white->black and black->white) since the sensor should
				# pass over 1 line while the robot is turning, the final
				# count should be 2
				count += above_line(self.ir.values[1]) ^ last_status
				last_status = above_line(self.ir.values[1])
		elif dir == 'R':
			# Turn right.
			self.motors.setSpeeds(TURN_SPEED, -TURN_SPEED)

			# This while loop monitors line position until the turn is complete.
			while( count < 2 ):
				self.ir.readLineBlack(); #was readLine()
				count += above_line(self.ir.values[4]) ^ last_status
				last_status = above_line(self.ir.values[4])
		elif dir == 'S':
	 		# Don't do anything!
			pass

	def select_turn( self, found_left, found_straight, found_right ):
		# This function decides which way to turn during the learning phase of
		# maze solving.  It uses the variables found_left, found_straight, and
		# found_right, which indicate whether there is an exit in each of the
		# three directions, applying the "left hand on the wall" strategy.

		# Make a decision about how to turn.  The following code
		# implements a left-hand-on-the-wall strategy, where we always
		# turn as far to the left as possible.
		if found_left:
			return 'L'
		elif found_straight:
			return 'S'
		elif found_right:
			return 'R'
		else:
			return 'B'

	def follow_segment( self ):
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
			position = self.ir.readLineBlack()

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
				self.motors.setSpeeds(SPEED + power_difference, SPEED)
			else:
				self.motors.setSpeeds(SPEED, SPEED - power_difference)

			# We use the inner four sensors (1, 2, 3, and 4) for
			# determining whether there is a line straight ahead, and the
			# sensors 0 and 5 for detecting lines going to the left and
			# right.

			if all( not(above_line(sensor)) for sensor in self.ir.values ):
				# There is no line visible ahead, and we didn't see any
				# intersection.  Must be a dead end.
				return
			elif above_line(self.ir.values[0]) or above_line(self.ir.values[5]):
			 	# Found an intersection.
				return

	def solve_maze( self ):
		# The solve_maze() function works by applying a "left hand on the wall" strategy:
		# the robot follows a segment until it reaches an intersection, where it takes the
		# leftmost fork available to it. It records each turn it makes, and as long as the
		# maze has no loops, this strategy will eventually lead it to the finish. Afterwards,
		# the recorded path is simplified by removing dead ends. More information can be
		# found in the 3pi maze solving example.
		while True:
			# Navigate current line segment
			self.follow_segment()

			# These variables record whether the robot has seen a line to the
			# left, straight ahead, and right, while examining the current
			# intersection.
			found_left = 0
			found_straight = 0
			found_right = 0

			# Now read the sensors and check the intersection type.
			#unsigned int sensors[6];
			self.ir.readLineBlack()

			# Check for left and right exits.
			if above_line(self.ir.values[0]):
				found_left = 1
			if above_line(self.ir.values[5]):
				found_right = 1

			# Drive straight a bit more, until we are  approximately in the middle
			# of intersection This should help us better detect if we
			# have left or right segments.
			self.motors.setSpeeds(SPEED, SPEED)
			time.sleep_ms( overshoot(LINE_THICKNESS)//2 )

			self.ir.readLineBlack()

			# Check for left and right exits.
			if above_line( self.ir.values[0] ):
			    found_left = 1
			if above_line( self.ir.values[5] ):
			    found_right = 1

			# After driving a little further, we
			# should have passed the intersection
			# and can check to see if we've hit the
			# finish line or if there is a straight segment ahead.
			time.sleep_ms( overshoot(LINE_THICKNESS)//2 )

			# Check for a straight exit.
			self.ir.readLineBlack()

			# Check again to see if left or right segment has been found
			if above_line( self.ir.values[0] ):
			    found_left = 1
			if above_line( self.ir.values[5] ):
			    found_right = 1

			if any( [ above_line(self.ir.values[i]) for i in range(1,5)] ):
				# if(above_line(sensors[1]) || above_line(sensors[2]) || above_line(sensors[3]) || above_line(sensors[4]))
				found_straight = 1

			# Check for the ending spot.
			# If all four middle sensors are on dark black, we have solved the maze.
			if all( [ above_line(self.ir.values[i]) for i in range(1,5	)] ):
				# if(above_line(sensors[1]) && above_line(sensors[2]) && above_line(sensors[3]) && above_line(sensors[4]))
				self.motors.stop()
				break

			# Intersection identification is complete.
			dir = self.select_turn( found_left, found_straight, found_right )

			# Make the turn indicated by the path.
			self.turn( dir )

			# Store the intersection in the path variable.
			self.path.append( dir )

			# You should check to make sure that the path_length does not
			# exceed the bounds of the array.  We'll ignore that in this example.

			# Simplify the learned path.
			self.simplify_path()

	def go_to_finish_line( self ):
		start = 0
		# Turn around if the Zumo is facing the wrong direction.
		if self.path[0] == 'B':
			self.turn('B')
			start=1

		for i in range( start, self.path_len ):
			self.follow_segment()

			# Drive through the intersection.
			self.motors.setSpeeds(SPEED, SPEED)
			time.sleep_ms( overshoot(LINE_THICKNESS) )
			self.motors.stop()

			# Make a turn according to the instruction stored in path[i].
			self.turn( self.path[i] )

		# Follow the last segment up to the finish.
		self.follow_segment()
		# The finish line has been reached.
		# Return and wait for another button push to restart the maze.
		self.ir.readLineBlack()
		self.motors.stop()

		return

	def simplify_path( self ):
		# simplifyPath analyzes the path[] array and reduces all the
		# turns. For example: Right turn + Right turn = (1) Back turn.

		# only simplify the path if the second-to-last turn was a 'B'
		if (self.path_len < 3) or not( self.path[self.path_len-2] == 'B' ):
			return

		total_angle = 0

		for i in range( 1, 4 ):
			_dir = self.path[ self.path_len - i ]
			if _dir == 'R':
				total_angle += 90
				break
			elif _dir == 'L':
				total_angle += 270
				break
			elif _dir == 'B':
				total_angle += 180
				break

		# Get the angle as a number between 0 and 360 degrees.
		total_angle = total_angle % 360

		# Replace all of those turns with a single one.
		if total_angle == 0:
			self.path[self.path_len - 3] = 'S'
		elif total_angle == 90:
			self.path[self.path_len - 3] = 'R'
		elif total_angle == 180:
			self.path[self.path_len - 3] = 'B'
		elif total_angle == 270:
			self.path[self.path_len - 3] = 'L'

		# The path is now two steps shorter.
		del( self.path[-1] )
		del( self.path[-1] )


# --- Setup --------------------------------------------------------------------
z = MazeSolver() # Desendant of ZumoShield

z.play_blip()
z.ir.emittersOn()
time.sleep_ms( 500 )
z.led.on()
z.button.waitForButton()

# Do calibration OR reload existing values
do_calibrate = False

# Reload calibration data
if do_calibrate:
	# Calibrate the Zumo by sweeping it from left to right
	# note: Replace the original Pololu code with a predefined one
	z.ir_calibration()
	# Turn left.
	z.turn('L')
	z.motors.stop()
	# Sound off buzzer to denote Zumo is finished calibrating
	z.buzzer.play("L16 cdegreg4")
else:
	# setup with your predefined calibration data
	z.ir.calibrationOn.load_json( '{"maximum": [2000, 2000, 1669, 1787, 2000, 2000], "minimum": [365, 365, 262, 260, 371, 371], "initialized": true}' )

# Turn off LED to indicate we are through with calibration
z.led.off()

# --- Loop ---------------------------------------------------------------------
# solve_maze() explores every segment of the maze until it finds the finish line.
z.solve_maze()
# Sound off buzzer to denote Zumo has solved the maze
z.play_2tones()

# The maze has been solved. When the user places the Zumo at the starting line
# and pushes the Zumo button, the Zumo knows where the finish line is and
# will automatically navigate.
while True:
	z.button.waitForButton()
	print( z.path )
	z.go_to_finish_line()
	#Sound off buzzer to denote Zumo is at the finish line.
	z.play_done()
