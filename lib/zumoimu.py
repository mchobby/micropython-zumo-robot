"""
zumoimu.py - easy library Pololu's Zumo Robot v1.3 IMU for MicroPython

* Author(s):    Braccio M.  from MCHobby (shop.mchobby.be).
                Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot

15 june 2022 - domeu - initial portage from ZumoIMU.cpp
"""

from micropython import const
import struct
import math
import time

LSM303DLHC_ACC_ADDR = const( 0b0011001 )
LSM303DLHC_MAG_ADDR = const( 0b0011110 )
LSM303D_ADDR   = const( 0b0011101 )
L3GD20H_ADDR   = const( 0b1101011 )
LSM6DS33_ADDR  = const( 0b1101011 )
LIS3MDL_ADDR   = const( 0b0011110 )

# Register address
LSM303DLHC_REG_CTRL_REG1_A  = const( 0x20 )
LSM303DLHC_REG_CTRL_REG4_A  = const( 0x23 )
LSM303DLHC_REG_STATUS_REG_A = const( 0x27 )
LSM303DLHC_REG_OUT_X_L_A    = const( 0x28 )

LSM303DLHC_REG_CRA_REG_M    = const( 0x00 )
LSM303DLHC_REG_CRB_REG_M    = const( 0x01 )
LSM303DLHC_REG_MR_REG_M     = const( 0x02 )
LSM303DLHC_REG_OUT_X_H_M    = const( 0x03 )
LSM303DLHC_REG_SR_REG_M     = const( 0x09 )

LSM303D_REG_STATUS_M  = const( 0x07 )
LSM303D_REG_OUT_X_L_M = const( 0x08 )
LSM303D_REG_WHO_AM_I  = const( 0x0F )
LSM303D_REG_CTRL1     = const( 0x20 )
LSM303D_REG_CTRL2     = const( 0x21 )
LSM303D_REG_CTRL5     = const( 0x24 )
LSM303D_REG_CTRL6     = const( 0x25 )
LSM303D_REG_CTRL7     = const( 0x26 )
LSM303D_REG_STATUS_A  = const( 0x27 )
LSM303D_REG_OUT_X_L_A = const( 0x28 )

L3GD20H_REG_WHO_AM_I = const( 0x0F )
L3GD20H_REG_CTRL1    = const( 0x20 )
L3GD20H_REG_CTRL4    = const( 0x23 )
L3GD20H_REG_STATUS   = const( 0x27 )
L3GD20H_REG_OUT_X_L  = const( 0x28 )

LSM6DS33_REG_WHO_AM_I   = const( 0x0F )
LSM6DS33_REG_CTRL1_XL   = const( 0x10 )
LSM6DS33_REG_CTRL2_G    = const( 0x11 )
LSM6DS33_REG_CTRL3_C    = const( 0x12 )
LSM6DS33_REG_STATUS_REG = const( 0x1E )
LSM6DS33_REG_OUTX_L_G   = const( 0x22 )
LSM6DS33_REG_OUTX_L_XL  = const( 0x28 )

LIS3MDL_REG_WHO_AM_I   = const( 0x0F )
LIS3MDL_REG_CTRL_REG1  = const( 0x20 )
LIS3MDL_REG_CTRL_REG2  = const( 0x21 )
LIS3MDL_REG_CTRL_REG3  = const( 0x22 )
LIS3MDL_REG_CTRL_REG4  = const( 0x23 )
LIS3MDL_REG_STATUS_REG = const( 0x27 )
LIS3MDL_REG_OUT_X_L    = const( 0x28 )

IMU_TYPE_Unknown = 0
IMU_TYPE_LSM303DLHC = 1       # LSM303DLHC accelerometer + magnetometer
IMU_TYPE_LSM303D_L3GD20H = 2  # LSM303D accelerometer + magnetometer, L3GD20H gyro
IMU_TYPE_LSM6DS33_LIS3MDL = 3 # LSM6DS33 gyro + accelerometer, LIS3MDL magnetometer


TEST_REG_ERROR  = const( -1 )

LSM303D_WHO_ID  = const( 0x49 )
L3GD20H_WHO_ID  = const( 0xD7 )
LSM6DS33_WHO_ID = const( 0x69 )
LIS3MDL_WHO_ID  = const( 0x3D )

class Vector:
	__slots__ = ['x','y','z']

	def __init__( self, x=None, y=None, z=None):
		"""" Create and init the vector with x,y,z parameters. x can also be a tuple with (x,y,z) values."""
		if type(x)==tuple: # Feeded with a tuple of 3 parameter (x,y,z)
			assert len(x)==3, "3 position required in tuple!"
			self.x = x[0]
			self.y = x[1]
			self.z = x[2]
		else:
			# Feeded with 3 NAMED parameter
			self.x=x
			self.y=y
			self.z=z

	def __repr__( self ):
		return "<%s %s,%s,%s>" % (self.__class__.__name__, self.x, self.y, self.z)

	def set( self, x=None, y=None, z=None ):
		""" Update the values which are not None in one operation. x can also be a tuple with (x,y,z) values."""
		if type(x)==tuple: # Feeded with a tuple of 3 parameter (x,y,z)
			assert len(x)==3, "3 position required in tuple!"
			if x[0]: self.x = x[0]
			if x[1]: self.y = x[1]
			if x[2]: self.z = x[2]
		else:
			# Feeded with 3 NAMED parameter
			if x: self.x = x
			if y: self.y = y
			if z: self.z = z

	@property
	def values( self ):
		return (self.x,self.y,self.z)

	def cross( self, b, out ):
		""" Cross operation with b Vector.  Update the out Vector """
		# vector_cross( a, b, out ) with a being the self vector
		# template <typename Ta, typename Tb, typename To> static void vector_cross(const vector<Ta> *a, const vector<Tb> *b, vector<To> *out);
		out.x = (self.y * b.z) - (self.z * b.y)
		out.y = (self.z * b.x) - (self.x * b.z)
		out.z = (self.x * b.y) - (self.y * b.x)

	def dot( self, b ):
		""" Dot operation with b Vector. Returns float """
		# def vector_dot( a, b ) with a being the self vector
		return (self.x * b.x) + (self.y * b.y) + (self.z * b.z)

	def normalize( self ):
		""" Normalize the vector and update its x,y,z values """
		mag = sqrt(self.dot(self)) # produce a float
		self.x /= mag
		self.y /= mag
		self.z /= mag

class ZumoIMU:
	""" Interfaces with the inertial sensors on the Zumo Shield """
	def __init__( self, i2c  ):
		self.i2c = i2c
		self.a = Vector( 0, 0, 0 ) # Int16, Raw Accelerometer reading
		self.g = Vector( 0, 0, 0 ) # Int16, Raw Gyro reading
		self.m = Vector( 0, 0, 0 ) # Int16, Raw magnetometer reading
		self._imu_type = IMU_TYPE_Unknown
		self.buf1 = bytearray( 1 )
		self.buf6 = bytearray( 6 )

		# see Arduino init() definition
		if self.__test_reg(LSM303DLHC_ACC_ADDR, LSM303DLHC_REG_CTRL_REG1_A) != TEST_REG_ERROR:
			# The DLHC doesn't have a documented WHO_AM_I register, so we test for it
			# by looking for a response at the DLHC accelerometer address. (The DLHC
			# magnetometer address is the same as that of the LIS3MDL.)
			self._imu_type = IMU_TYPE_LSM303DLHC
		elif ( self.__test_reg(LSM303D_ADDR, LSM303D_REG_WHO_AM_I) == LSM303D_WHO_ID ) and ( self.__test_reg(L3GD20H_ADDR, L3GD20H_REG_WHO_AM_I) == L3GD20H_WHO_ID) :
			self._imu_type = IMU_TYPE_LSM303D_L3GD20H
		elif ( self.__test_reg( LSM6DS33_ADDR, LSM6DS33_REG_WHO_AM_I) == LSM6DS33_WHO_ID ) and ( self.__test_reg( LIS3MDL_ADDR,  LIS3MDL_REG_WHO_AM_I) ==  LIS3MDL_WHO_ID) :
			self._imu_type = IMU_TYPE_LSM6DS33_LIS3MDL
		else:
			raise Exception( "IMU detection failed" )

		# initialize the default
		self.enable_default()


	def enable_default( self ):
		if self._imu_type == IMU_TYPE_LSM303DLHC:
			# --- Accelerometer ---
			# 0x47 = 0b01000111
			# ODR = 0100 (50 Hz ODR); Zen = Yen = Xen = 1 (all axes enabled)
			self.__write_reg(LSM303DLHC_ACC_ADDR, LSM303DLHC_REG_CTRL_REG1_A, 0x47)
			# 0x08 = 0b00001000
			# FS = 00 (+/- 2 g full scale); HR = 1 (high resolution enable)
			self.__write_reg(LSM303DLHC_ACC_ADDR, LSM303DLHC_REG_CTRL_REG4_A, 0x08)
			# --- Magnetometer ---
			# 0x0C = 0b00001100
			# DO = 011 (7.5 Hz ODR)
			self.__write_reg(LSM303DLHC_MAG_ADDR, LSM303DLHC_REG_CRA_REG_M, 0x0C)
			# 0x80 = 0b10000000
			# GN = 100 (+/- 4 gauss full scale)
			self.__write_reg(LSM303DLHC_MAG_ADDR, LSM303DLHC_REG_CRB_REG_M, 0x80)
			# 0x00 = 0b00000000
			# MD = 00 (continuous-conversion mode)
			self.__write_reg(LSM303DLHC_MAG_ADDR, LSM303DLHC_REG_MR_REG_M, 0x00)

		elif self._imu_type == IMU_TYPE_LSM303D_L3GD20H:
			# --- Accelerometer ---
			# 0x57 = 0b01010111
			# AODR = 0101 (50 Hz ODR); AZEN = AYEN = AXEN = 1 (all axes enabled)
			self.__write_reg(LSM303D_ADDR, LSM303D_REG_CTRL1, 0x57)
			# 0x00 = 0b00000000
			# AFS = 0 (+/- 2 g full scale)
			self.__write_reg(LSM303D_ADDR, LSM303D_REG_CTRL2, 0x00)
			# --- Magnetometer ---
			# 0x64 = 0b01100100
			# M_RES = 11 (high resolution mode); M_ODR = 001 (6.25 Hz ODR)
			self.__write_reg(LSM303D_ADDR, LSM303D_REG_CTRL5, 0x64)
			# 0x20 = 0b00100000
			# MFS = 01 (+/- 4 gauss full scale)
			self.__write_reg(LSM303D_ADDR, LSM303D_REG_CTRL6, 0x20)
			# 0x00 = 0b00000000
			# MD = 00 (continuous-conversion mode)
			self.__write_reg(LSM303D_ADDR, LSM303D_REG_CTRL7, 0x00)
			# --- Gyro ---
			# 0x7F = 0b01111111
			# DR = 01 (189.4 Hz ODR); BW = 11 (70 Hz bandwidth); PD = 1 (normal mode); Zen = Yen = Xen = 1 (all axes enabled)
			self.__write_reg(L3GD20H_ADDR, L3GD20H_REG_CTRL1, 0x7F)
			# 0x00 = 0b00000000
			# FS = 00 (+/- 245 dps full scale)
			self.__write_reg(L3GD20H_ADDR, L3GD20H_REG_CTRL4, 0x00)

		elif self._imu_type == IMU_TYPE_LSM6DS33_LIS3MDL:
			# --- Accelerometer ---
			# 0x30 = 0b00110000
			# ODR = 0011 (52 Hz (high performance)); FS_XL = 00 (+/- 2 g full scale)
			self.__write_reg(LSM6DS33_ADDR, LSM6DS33_REG_CTRL1_XL, 0x30)
			# --- Gyro ---
			# 0x50 = 0b01010000
			# ODR = 0101 (208 Hz (high performance)); FS_G = 00 (+/- 245 dps full scale)
			self.__write_reg(LSM6DS33_ADDR, LSM6DS33_REG_CTRL2_G, 0x50)
 			# --- Accelerometer + Gyro ---
			# 0x04 = 0b00000100
			# IF_INC = 1 (automatically increment register address)
			self.__write_reg(LSM6DS33_ADDR, LSM6DS33_REG_CTRL3_C, 0x04)
			# --- Magnetometer ---
			# 0x70 = 0b01110000
			# OM = 11 (ultra-high-performance mode for X and Y); DO = 100 (10 Hz ODR)
			self.__write_reg(LIS3MDL_ADDR, LIS3MDL_REG_CTRL_REG1, 0x70)
			# 0x00 = 0b00000000
			# FS = 00 (+/- 4 gauss full scale)
			self.__write_reg(LIS3MDL_ADDR, LIS3MDL_REG_CTRL_REG2, 0x00)
			# 0x00 = 0b00000000
			# MD = 00 (continuous-conversion mode)
			self.__write_reg(LIS3MDL_ADDR, LIS3MDL_REG_CTRL_REG3, 0x00)
			# 0x0C = 0b00001100
			# OMZ = 11 (ultra-high-performance mode for Z)
			self.__write_reg(LIS3MDL_ADDR, LIS3MDL_REG_CTRL_REG4, 0x0C)


	def __test_reg( self, addr, reg ):
		try:
			self.i2c.readfrom_mem_into( addr, reg, self.buf1 )
			return self.buf1[0]
		except:
			return TEST_REG_ERROR

	def __read_axes( self, addr, first_reg, vector, endianness="<hhh" ):
		# read 16 bits axes and populate "vector", assume we are in little-endian by default
		self.i2c.readfrom_mem_into( addr, first_reg, self.buf6 )
		vector.x, vector.y, vector.z = struct.unpack( endianness, self.buf6 )

	def __write_reg( self, addr, reg, value ):
		self.buf1[0] = value
		self.i2c.writeto_mem( addr, reg, self.buf1 )

	@property
	def imu_type( self ):
		return self._imu_type

	def config_for_compass_heading( self ):
		# Configures the sensors with settings optimized for determining a
		# compass heading with the magnetometer
		if self._imu_type == IMU_TYPE_LSM303DLHC:
			# --- Magnetometer ---
			# 0x18 = 0b00011000
			# DO = 110 (75 Hz ODR)
			self.__write_reg(LSM303DLHC_MAG_ADDR, LSM303DLHC_REG_CRA_REG_M, 0x18)
		elif self._imu_type == IMU_TYPE_LSM303D_L3GD20H:
			# --- Magnetometer ---
			# 0x64 = 0b01110000
			# M_RES = 11 (high resolution mode); M_ODR = 100 (50 Hz ODR)
			self.__write_reg(LSM303D_ADDR, LSM303D_REG_CTRL5, 0x70)
		elif self._imu_type == IMU_TYPE_LSM6DS33_LIS3MDL:
			# --- Magnetometer ---
			# 0x7C = 0b01111100
			# OM = 11 (ultra-high-performance mode for X and Y); DO = 111 (80 Hz ODR)
			self.__write_reg(LIS3MDL_ADDR, LIS3MDL_REG_CTRL_REG1, 0x7C)


	def read_acc( self ):
		#  Reads the 3 accelerometer channels and stores them in vector a
		if self._imu_type == IMU_TYPE_LSM303DLHC:
			# set MSB of register address for auto-increment
			self.__read_axes( LSM303DLHC_ACC_ADDR, LSM303DLHC_REG_OUT_X_L_A | (1 << 7), self.a )
		elif self._imu_type == IMU_TYPE_LSM303D_L3GD20H:
			# set MSB of register address for auto-increment
			self.__read_axes( LSM303D_ADDR, LSM303D_REG_OUT_X_L_A | (1 << 7), self.a )
		elif self._imu_type == IMU_TYPE_LSM6DS33_LIS3MDL:
			# assumes register address auto-increment is enabled (IF_INC in CTRL3_C)
			self.__read_axes( LSM6DS33_ADDR, LSM6DS33_REG_OUTX_L_XL, self.a )


	def read_mag( self ):
		if self._imu_type == IMU_TYPE_LSM303DLHC:
			# read_axes assumes the sensor axis outputs are little-endian and in
			# XYZ order. However, the DLHC magnetometer outputs are big-endian and in
			# XZY order, so we need to shuffle things around here...
			self.read_axes( LSM303DLHC_MAG_ADDR, LSM303DLHC_REG_OUT_X_H_M, self.m,  endianness=">hhh")
			self.m.y, self.m.z = self.m.y, self.m.z
		elif self._imu_type == IMU_TYPE_LSM303D_L3GD20H:
			# set MSB of register address for auto-increment
			self.read_axes( LSM303D_ADDR, LSM303D_REG_OUT_X_L_M | (1 << 7), self.m )
		elif self._imu_type == IMU_TYPE_LSM6DS33_LIS3MDL:
			# set MSB of register address for auto-increment
			self.__read_axes( LIS3MDL_ADDR, LIS3MDL_REG_OUT_X_L | (1 << 7), self.m )


	def read_gyro( self ):
		if self._imu_type == IMU_TYPE_LSM303D_L3GD20H:
			# set MSB of register address for auto-increment
			self.__read_axes( L3GD20H_ADDR, L3GD20H_REG_OUT_X_L | (1 << 7), self.g )
		elif self._imu_type == IMU_TYPE_LSM6DS33_LIS3MDL:
			# assumes register address auto-increment is enabled (IF_INC in CTRL3_C)
			self.__read_axes( LSM6DS33_ADDR, LSM6DS33_REG_OUTX_L_G, self.g )


	def read( self ):
		# read all 3 sensors
		self.read_acc()
		self.read_gyro()
		self.read_mag()

	@property
	def mag_data_ready( self ):
		if self._imu_type == IMU_TYPE_LSM303DLHC:
			return semf.__read_reg( LSM303DLHC_MAG_ADDR, LSM303DLHC_REG_SR_REG_M) & 0x01 > 0
		elif self._imu_type == IMU_TYPE_LSM303D_L3GD20H:
			return self.__read_reg( LSM303D_ADDR, LSM303D_REG_STATUS_M) & 0x08 > 0
		elif self._imu_type == IMU_TYPE_LSM6DS33_LIS3MDL:
			return self.__read_reg( LIS3MDL_ADDR, LIS3MDL_REG_STATUS_REG) & 0x08 > 0

		return False

	@property
	def acc_data_ready( self ):
		if self._imu_type == IMU_TYPE_LSM303DLHC:
			return self.__read_reg( LSM303DLHC_ACC_ADDR, LSM303DLHC_REG_STATUS_REG_A) & 0x08 > 0
		elif self._imu_type == LSM303D_L3GD20H:
			return self.__read_reg( LSM303D_ADDR, LSM303D_REG_STATUS_A) & 0x08 > 0
		elif self._imu_type == LSM6DS33_LIS3MDL:
			return self.__read_reg( LSM6DS33_ADDR, LSM6DS33_REG_STATUS_REG) & 0x01 > 0

		return False

	@property
	def gyro_data_ready( self ):
		if self._imu_type == IMU_TYPE_LSM303D_L3GD20H:
			return self.__read_reg( L3GD20H_ADDR, L3GD20H_REG_STATUS) & 0x08 > 0
		elif self._imu_type == IMU_TYPE_LSM6DS33_LIS3MDL:
			return self.__read_reg( LSM6DS33_ADDR, LSM6DS33_REG_STATUS_REG) & 0x02 > 0

		return False

class Compass( object ):
	""" Compass IMU offers some COMPAS utility method over the IMU """
	CALIBRATION_SAMPLES = 70
	DEVIATION_THRESHOLD = 5

	def __init__( self, imu ):
		self._imu = imu
		self._imu.config_for_compass_heading()
		self._avg = Vector(0,0,0)
		self.m_min = Vector(32767,32767,32767)    # Used to calibrate min & max on magnetic sensor
		self.m_max = Vector(-32767,-32767,-32767)

	@property
	def min( self ):
		""" Calibration minima """
		return self.m_min

	@property
	def max( self ):
		""" Calibration maxima """
		return self.m_max

	def calibrate( self ):
		""" Magnetic sensor must turn on himself while performing  min & max values sampling """
		self.m_min = Vector(32767,32767,32767)
		self.m_max = Vector(-32767,-32767,-32767)

		for x in range( self.CALIBRATION_SAMPLES):
			self._imu.read_mag()
			self.m_min.x = min(self.m_min.x, self._imu.m.x)
			self.m_min.y = min(self.m_min.y, self._imu.m.y)

			self.m_max.x = max(self.m_max.x, self._imu.m.x)
			self.m_max.y = max(self.m_max.y, self._imu.m.y)
			print("COMPTEUR: %s | Running_max: %s | Running_min: %s " %(x, self.m_max, self.m_min))

			time.sleep_ms(50)

	def averageHeading( self ):
		self._avg.set( 0,0,0 )
		for x in range(10):
			self._imu.read_mag()
			self._avg.x += self._imu.m.x
			self._avg.y += self._imu.m.y

		self._avg.x /= 10.0
		self._avg.y /= 10.0

		return self.heading() # angle in degree

	def relativeHeading( self, heading_from, heading_to):
		relative_heading=float(heading_to) - float(heading_from)
		if relative_heading > 180:
			relative_heading -=	360
		if  relative_heading < -180:
			relative_heading +=360

		return relative_heading

	def heading( self ):
		x_scaled = 2.0*(self._avg.x - self.m_min.x)/(self.m_max.x - self.m_min.x) - 1.0
		y_scaled = 2.0*(self._avg.y - self.m_min.y)/(self.m_max.y - self.m_min.y) - 1.0

		angle = math.atan2(y_scaled, x_scaled)*180/ math.pi # Radian
		if angle < 0 :
			angle+= 360
		return angle
