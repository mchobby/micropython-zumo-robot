"""
qtrsensors.py - easy library for Pololu Reflectance Sensors for MicroPython

* Author(s):    Braccio M.  from MCHobby (shop.mchobby.be).
                Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot
See example line_follower.py in the project source

History:
  21 jul 2021 - Braccio M. - Initial writing
  20 jul 2022 - Meurisse D. - Complete rewriting
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

from micropython import const
from machine import Pin
import time

# QTRReadMode
# https://github.com/pololu/qtr-sensors-arduino/blob/master/QTRSensors.h
READMODE_OFF = const(0)
READMODE_ON = const(1)
READMODE_ON_AND_OFF = const(2)
READMODE_ODD_EVEN = const(3)
READMODE_ODD_EVEN_AND_OFF = const(4)
READMODE_MANUAL = const(5)

# QTREmitters
EMITTERS_ALL = const(0)
EMITTERS_ODD = const(1)
EMITTERS_EVEN= const(2)
EMITTERS_NONE= const(3)

NO_EMITTER_PIN = None

DEFAULT_TIMEOUT = const(2500) # uSec

MAX_SENSOR = const(31)

class CalibrationData:
	def __init__( self ):
		self.initialized = False
		self.minimum = None
		self.maximum = None


class QTRSensors(object):
	def __init__(self,pins,emitterPin, evenEmitterPin=None, timeout=DEFAULT_TIMEOUT):
		assert len(pins) < MAX_SENSOR
		self._sensorPins = pins
		self._sensorCount = len( pins )

		self._timeout = timeout # only used for RC sensors
		self._maxValue = timeout # the maximum value returned by readPrivate()
		# self._samplesPerSensor = 4 # only used for analog sensors
		self.calibrationOn = CalibrationData()
		self.calibrationOff = CalibrationData()

		self._oddEmitterPin = emitterPin # also used for single emitter pin
		self._evenEmitterPin = evenEmitterPin
		self._emitterPinCount = 1 + 1 if evenEmitterPin != None else 0 # at least one
		self._oddEmitterPin.init( Pin.OUT )
		if self._evenEmitterPin != None:
			self._evenEmitterPin.init( Pin.OUT )

		self._dimmable = True
		self._dimmingLevel = 0

		self._lastPosition = 0


	def __emittersOnWithPin( self, pin ): #pin:uint8_t return:uint16_t
		if self._dimmable and (pin.value() == 1) :
			# We are turning on dimmable emitters that are already on. To avoid messing
			# up the dimming level, we have to turn the emitters off and back on. This
			# means the turn-off delay will happen even if wait = false was passed to
			# emittersOn(). (Driver min is 1 ms.)
			pin.value( 0 )
			time.sleep_us(1200)

		pin.value(1)
		emittersOnStart = time.ticks_us()

		if self._dimmable and (self._dimmingLevel > 0):
			# noInterrupts();
			for i in range( self._dimmingLevel ): #(uint8_t i = 0; i < _dimmingLevel; i++)
				time.sleep_us(1)
				pin.value(0)
				time.sleep_us(1)
				pin.value(1)
			# interrupts();

		return emittersOnStart

	def __calibrateOnOrOff( self, calibration, mode ): # CalibrationData & calibration, QTRReadMode mode):
		# Handles the actual calibration, including (re)allocating and
		# initializing the storage for the calibration values if necessary.
		sensorValues = [0]*self._sensorCount
		maxSensorValues = [0]*self._sensorCount
		minSensorValues = [0]*self._sensorCount

		# (Re)allocate and initialize the arrays if necessary.
		if not calibration.initialized:
			# Looks not used! oldMaximum = list( calibration.maximum ) # Make a copy
			calibration.maximum = [0]*self._sensorCount

			# Looks not used! oldMinimum = list(calibration.minimum) # Make a copy
			calibration.minimum = [self._maxValue]*self._sensorCount
			calibration.initialized = True


		for j in range( 10 ): # (uint8_t j = 0; j < 10; j++)
			self.read(sensorValues, mode)
			for i in range( self._sensorCount ): # (uint8_t i = 0; i < _sensorCount; i++)
				# set the max we found THIS time
				if (j == 0) or (sensorValues[i] > maxSensorValues[i]) :
					maxSensorValues[i] = sensorValues[i]
				# set the min we found THIS time
				if (j == 0) or (sensorValues[i] < minSensorValues[i]) :
					minSensorValues[i] = sensorValues[i]

		# record the min and max calibration values
		for i in range( self._sensorCount ):
			# Update maximum only if the min of 10 readings was still higher than it
			# (we got 10 readings in a row higher than the existing maximum).
			if minSensorValues[i] > calibration.maximum[i]:
				calibration.maximum[i] = minSensorValues[i]

			# Update minimum only if the max of 10 readings was still lower than it
			# (we got 10 readings in a row lower than the existing minimum).
			if maxSensorValues[i] < calibration.minimum[i]:
				calibration.minimum[i] = maxSensorValues[i]

	def __readPrivate( self, sensorValues, start = 0, step = 1): # uint16_t * sensorValues, uint8_t start = 0, uint8_t step = 1
		# ONLY SUPPORTS the RC sensor (not analog ones)
		# Reads the first of every [step] sensors, starting with [start] (0-indexed, so start = 0 means start with the first sensor).
		# For example, step = 2, start = 1 means read the *even-numbered* sensors. start defaults to 0, step defaults to 1
		if self._sensorPins == None:
			return

		for i in range( start, self._sensorCount, step ): #(uint8_t i = start; i < _sensorCount; i += step)
			sensorValues[i] = self._maxValue
			# make sensor line an output (drives low briefly, but doesn't matter)
			self._sensorPins[i].init( Pin.OUT )
			# drive sensor line high
			self._sensorPins[i].value( 1 )

		time.sleep_us(10) # charge lines for 10 us

		# disable interrupts so we can switch all the pins as close to the same time as possible
		# noInterrupts()

		# record start time before the first sensor is switched to input
		# (similarly, time is checked before the first sensor is read in the loop below)
		startTime = time.ticks_us()
		_time = 0

		for i in range( start, self._sensorCount, step ): # (uint8_t i = start; i < _sensorCount; i += step)
			#make sensor line an input (should also ensure pull-up is disabled)
			self._sensorPins[i].init( Pin.IN )

		# interrupts() # re-enable
		_time = time.ticks_diff( time.ticks_us(), startTime )
		while _time < self._maxValue:
			# disable interrupts so we can read all the pins as close to the same
			# time as possible
			#noInterrupts()
			for i in range( start, self._sensorCount, step ): # (uint8_t i = start; i < _sensorCount; i += step)
				if (self._sensorPins[i].value() == 0) and (_time < sensorValues[i]):
					# record the first time the line reads low
					sensorValues[i] = _time
			_time = time.ticks_diff( time.ticks_us(), startTime )
		# interrupts() # re-enable

	def __readLinePrivate( self, sensorValues, mode, invertReadings): # returns uint16_t, uint16_t * sensorValues, QTRReadMode mode, bool invertReadings
		onLine = False # Sensor is on the line
		avg = 0 # this is for the weighted total
		sum = 0 # this is for the denominator, which is <= 64000

		# manual emitter control is not supported
		if mode == READMODE_MANUAL:
			return 0

		self.readCalibrated( sensorValues, mode )

		for i in range( self._sensorCount ): # (uint8_t i = 0; i < _sensorCount; i++)
			value = sensorValues[i]
			if invertReadings:
				value = 1000 - value

			# keep track of whether we see the line at all
			if value > 200:
				onLine = True

			# only average in values that are above a noise threshold
			if value > 50:
				avg += int(value * i * 1000)
				sum += value

		if not onLine:
			# If it last read to the left of center, return 0.
			if self._lastPosition < (self._sensorCount - 1) * 1000 / 2:
				return 0
			# If it last read to the right of center, return the max.
			else:
				return (self._sensorCount - 1) * 1000

		self._lastPosition = int(avg / sum)
		return self._lastPosition

	# Ignored: void setTypeRC();
	# Ignored: void setTypeAnalog();
	# Ignored: QTRType getType() { return _type; }

	@property
	def sensorPins( self ):
		return self._sensorPins

	@property
	def emitterPin( self ): # When only one Pin to control them all (it is the odd reference)
		# Assigned only at creation time
		return self._oddEmitterPin
	@property
	def oddEmitterPin( self ):
		# Assigned only at creation time
		return self._oddEmitterPin
	@property
	def evenEmitterPin( self ):
		# Assigned only at creation time
		return self._evenEmitterPin
	@property
	def emitterPinCount( self ):
		return self._emitterPinCount

	@property
	def timeout( self ):
		# recommanded value between 1000 & 3000 uSec
		return self._timeout
	@timeout.setter
	def timeout( self, value ):
		assert 0<=value<=5000
		self._timeout = value


	@property
	def dimmable(self):
		return self._dimmable
	@dimmable.setter
	def dimmable(self, value):
		self._dimmable = value

	@property
	def dimmingLevel(self):
		return self._dimmingLevel
	@dimmingLevel.setter
	def dimmingLevel( self, value ):
		assert 0<=value<=31
		self._dimmingLevel = value

	def emittersOff( self, emitters=EMITTERS_ALL, wait=True ):
		""" mainly used by read to switch emitter on/off, all or partial """
		assert emitters in (EMITTERS_ALL,EMITTERS_ODD,EMITTERS_EVEN)

		pinChanged = False
		# Use odd emitter pin in these cases:
		# - 1 emitter pin, emitters = all
		# - 2 emitter pins, emitters = all
		# - 2 emitter pins, emitters = odd
		if (emitters==EMITTERS_ALL) or ((self._emitterPinCount==2) and (emitters==EMITTERS_ODD)):
			# Check if pin is defined and only turn off if not already off
			if (self._oddEmitterPin != None) and ( self._oddEmitterPin.value() == 1 ):
				self._oddEmitterPin.value( 0 )
				pinChanged = True


		# Use even emitter pin in these cases:
		# - 2 emitter pins, emitters = all
		# - 2 emitter pins, emitters = even
		if (self._emitterPinCount == 2) and (emitters in (EMITTERS_ALL, EMITTERS_EVEN)) :
		 	# Check if pin is defined and only turn off if not already off
			if ( self._evenEmitterPin != None) and ( self._evenEmitterPin.value() == 1 ):
			  self._evenEmitterPin.value( 0 )
			  pinChanged = True

		if wait and pinChanged :
			if self._dimmable:
				# driver min is 1 ms
				time.sleep_us(1200)
			else:
				time.sleep_us(200)


	def emittersOn( self, emitters=EMITTERS_ALL, wait=True ):
		assert emitters in (EMITTERS_ALL,EMITTERS_ODD,EMITTERS_EVEN)
		pinChanged = False
		emittersOnStart = 0 # uint16_t ;

		# Use odd emitter pin in these cases:
		# - 1 emitter pin, emitters = all
		# - 2 emitter pins, emitters = all
		# - 2 emitter pins, emitters = odd
		if (emitters == EMITTERS_ALL) or ((self._emitterPinCount == 2) and (emitters == EMITTERS_ODD)):
			# Check if pin is defined, and only turn on non-dimmable sensors if not
			# already on, but always turn dimmable sensors off and back on because
			# we might be changing the dimming level (emittersOnWithPin() should take
			# care of this)
			if (self._oddEmitterPin != None) and ( self._dimmable or (self._oddEmitterPin.value() == 0)):
				emittersOnStart = self.__emittersOnWithPin(self._oddEmitterPin)
				pinChanged = True

		# Use even emitter pin in these cases:
		# - 2 emitter pins, emitters = all
		# - 2 emitter pins, emitters = even
		if (self._emitterPinCount == 2) and ((emitters == EMITTERS_ALL) or (emitters == EMITTERS_EVEN)):
			# Check if pin is defined, and only turn on non-dimmable sensors if not
			# already on, but always turn dimmable sensors off and back on because
			# we might be changing the dimming level (emittersOnWithPin() should take care of this)
			if (self._evenEmitterPin != None) and ((self._dimmable) or (self._evenEmitterPin.value() == 0)):
				emittersOnStart = self.__emittersOnWithPin(self._evenEmitterPin)
				pinChanged = True

		if wait and pinChanged:
			if self._dimmable:
				# Make sure it's been at least 300 us since the emitter pin was first set
				# high before returning. (Driver min is 250 us.) Some time might have
				# already passed while we set the dimming level.
				while time.ticks_diff( time.ticks_us(), emittersOnStart) < 300 :
					time.sleep_us(10)
			else: # not dimmable
				time.delay_us(200)

	def emittersSelect( self, emitters ):
		""" Turn on selected emitters and turns off the other """
		assert emitters in (EMITTERS_ALL,EMITTERS_ODD,EMITTERS_EVEN,EMITTERS_NONE)
		offEmitters = None

		if emitters==EMITTERS_ODD:
			offEmitters = EMITTERS_EVEN
		elif emitters==EMITTERS_EVEN:
			offEmitters = EMITTERS_ODD
		elif emitters==EMITTERS_ALL:
			self.emittersOn()
			return
		elif emitters==EMITTERS_NONE:
			self.emittersOff()
			return
		else: # invalid
			return

		# Turn off the off-emitters; don't wait before proceeding, but record the time.
		self.emittersOff( offEmitters, False )
		turnOffStart = time.ticks_us()

		# Turn on the on-emitters and wait.
		self.emittersOn( emitters )

		if self._dimmable:
			# Finish waiting for the off-emitters emitters to turn off: make sure it's been
			# at least 1200 us since the off-emitters was turned off before returning.
			# (Driver min is 1 ms.) Some time has already passed while we waited for
			# the on-emitters to turn on.
			while ticks_diff( time.ticks_us(), turnOffStart ) < 1200:
				time.delay_us(10)


	def calibrate( self, mode=READMODE_ON ):
		""" Read the sensor for calibration. Mode indicates the emitter behavior
		    during the calibration. Manual emitter control is not supported  """
		assert mode in (READMODE_OFF, READMODE_ON, READMODE_ON_AND_OFF, READMODE_ODD_EVEN, READMODE_ODD_EVEN_AND_OFF, READMODE_MANUAL )

		if mode == READMODE_MANUAL:
			return

		if mode in (READMODE_ON, READMODE_ON_AND_OFF ):
			self.__calibrateOnOrOff( self.calibrationOn, READMODE_ON )
		elif mode in (READMODE_ODD_EVEN, READMODE_ODD_EVEN_AND_OFF):
			self.__calibrateOnOrOff( self.calibrationOn, READMODE_ODD_EVEN )

		if mode in (READMODE_ON_AND_OFF, READMODE_ODD_EVEN_AND_OFF, READMODE_OFF):
			self.__calibrateOnOrOff( self.calibrationOff, READMODE_OFF)


	def resetCalibration( self ):
		for i in range(self._sensorCount): #(uint8_t i = 0; i < _sensorCount; i++)
			if self.calibrationOn.maximum != None:
				self.calibrationOn.maximum[i] = 0
			if self.calibrationOff.maximum!= None:
				self.calibrationOff.maximum[i] = 0
			if self.calibrationOn.minimum != None:
				self.calibrationOn.minimum[i] = self._maxValue
			if self.calibrationOff.minimum!= None:
				self.calibrationOff.minimum[i] = self._maxValue


	def read( self, sensorValues, mode=READMODE_ON ):
		assert mode in (READMODE_OFF, READMODE_ON, READMODE_ON_AND_OFF, READMODE_ODD_EVEN, READMODE_ODD_EVEN_AND_OFF, READMODE_MANUAL )
		if mode==READMODE_OFF:
			self.emittersOff()
			self.__readPrivate( sensorValues )
			return
		elif mode==READMODE_MANUAL:
			self.__readPrivate( sensorValues )
			return
		elif mode in ( READMODE_ON, READMODE_ON_AND_OFF ):
			self.emittersOn();
			self.__readPrivate( sensorValues )
			self.emittersOff()
		elif mode in ( READMODE_ODD_EVEN , READMODE_ODD_EVEN_AND_OFF ):
			# Turn on odd emitters and read the odd-numbered sensors.
			# (readPrivate takes a 0-based array index, so start = 0 to start with the first sensor)
			self.emittersSelect(READMODE_ODD)
			self.__readPrivate(sensorValues, 0, 2)
			# Turn on even emitters and read the even-numbered sensors.
			# (readPrivate takes a 0-based array index, so start = 1 to start with  the second sensor)
			self.emittersSelect(READMODE_EVEN)
			self.__readPrivate(sensorValues, 1, 2)
			self.emittersOff()
		else:
			# invalid - do nothing
			return

		if mode in (READMODE_ON_AND_OFF, READMODE_ODD_EVEN_AND_OFF):
			#Take a second set of readings and return the values (on + max - off).
			offValues = [0]*self._sensorCount
			self.__readPrivate(offValues)
			for i in range( self._sensorCount ):
				 sensorValues[i] += self._maxValue - offValues[i]
				 if sensorValues[i] > _maxValue:
					# This usually doesn't happen, because the sensor reading should
				 	# go up when the emitters are turned off.
					sensorValues[i] = self._maxValue


	def readCalibrated( self, sensorValues, mode=READMODE_ON ):
		assert mode in (READMODE_OFF, READMODE_ON, READMODE_ON_AND_OFF, READMODE_ODD_EVEN, READMODE_ODD_EVEN_AND_OFF, READMODE_MANUAL )
		# manual emitter control is not supported
		if mode == READMODE_MANUAL:
			return

		# if not calibrated, do nothing
		if mode in (READMODE_ON,READMODE_ON_AND_OFF,READMODE_ODD_EVEN_AND_OFF):
			if not self.calibrationOn.initialized:
				return

		if mode in (READMODE_OFF, READMODE_ON_AND_OFF, READMODE_ODD_EVEN_AND_OFF):
			if not self.calibrationOff.initialized:
				return

		# read the needed values
		self.read( sensorValues, mode )

		for i in range( self._sensorCount ):
			calmin = self._maxValue
			calmax = 0

			# find the correct calibration
			if mode in (READMODE_ON,READMODE_ODD_EVEN):
				calmax = self.calibrationOn.maximum[i]
				calmin = self.calibrationOn.minimum[i]
			elif (mode == READMODE_OFF):
				calmax = self.calibrationOff.maximum[i]
				calmin = self.calibrationOff.minimum[i]
			else: # READMODE_ON_AND_OFF, READMODE_ODD_EVEN_AND_OFF
				if self.calibrationOff.minimum[i] < self.calibrationOn.minimum[i]:
					# no meaningful signal
					calmin = self._maxValue
				else:
					# this won't go past _maxValue
					calmin = self.calibrationOn.minimum[i] + self._maxValue - self.calibrationOff.minimum[i]

				if self.calibrationOff.maximum[i] < self.calibrationOn.maximum[i]:
					# no meaningful signal
					calmax = self._maxValue
				else:
					#this won't go past _maxValue
					calmax = self.calibrationOn.maximum[i] + self._maxValue - self.calibrationOff.maximum[i];

			denominator = calmax - calmin
			value = 0
			if denominator != 0:
				value = int((sensorValues[i] - calmin) * 1000 / denominator)

			if value < 0:
				value = 0
			elif value > 1000:
				value = 1000

			sensorValues[i] = value


	def readLineBlack( self, sensorValues, mode=READMODE_ON ):
		""" Reads the sensors, provides calibrated values, and returns an
			estimated black line position. """
		return self.__readLinePrivate( sensorValues, mode, False )

	def readLineWhite( self, sensorValues, mode=READMODE_ON ):
		""" Reads the sensors, provides calibrated values, and returns an
			estimated white line position. """
		self.__readLinePrivate( sensorValues, mode, True )

class QTRSensorsAnalog(object):
    """this class isn't used in this projet. The original arduino library can be found on: https://github.com/pololu/qtr-sensors-arduino/releases"""
    pass
