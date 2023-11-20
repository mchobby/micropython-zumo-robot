""" RFM69 RC Zumo : RECEIVER - remote controled ZUMO

Receives message over RFM69HCW SPI module - RC RECEIVER node
Must be used with with rfm_rc_joy.py

See project source @ https://github.com/mchobby/micropython-zumo-robot

30 june 2023 - domeu - initial writing
"""

from zumoshield import *
from machine import Pin, SPI
from rfm69 import RFM69
import time


FREQ           = 433.1
ENCRYPTION_KEY = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
NODE_ID        = 100 # ID of this my node node

# RFM Interface
spi = SPI(0, miso=Pin(4), mosi=Pin(7), sck=Pin(6), polarity=0, phase=0, firstbit=SPI.MSB) # baudrate=50000,
nss = Pin( 5, Pin.OUT, value=True )
rst = Pin( 22, Pin.OUT, value=False )

rfm = RFM69( spi=spi, nss=nss, reset=rst )
rfm.frequency_mhz = FREQ
rfm.encryption_key = ( ENCRYPTION_KEY )
rfm.node = NODE_ID # This instance is the node 123


SPEED_CENTER_US = 1489
DIR_CENTER_US = 1551
RANGE_US = 400

#ch_speed  = Pin( 7, Pin.IN ) # ch 3
#ch_dir = Pin( 6, Pin.IN )    #


def map(value, istart, istop, ostart, ostop):
  return ostart + (ostop - ostart) * ((value - istart) / (istop - istart))

# Joystick information
joy_xpos = 65535//2
joy_ypos = 65535//2
joy_btn = 0

z = ZumoShield()
z.play_blip()
while True:
	# Try to receive a packet.
	packet = rfm.receive()
	if packet is None:
		# Packet has not been received
		continue
	else:
		# Received a packet!
		packet_text = str(packet, "ascii")
		_l = packet_text.split(",")
		if len(_l)!=3:
			z.led.toggle()
			continue
		try:
			joy_xpos = int(_l[0])
			joy_ypos = int(_l[1])
			joy_btn = int(_l[2])
		except:
			z.led.toggle()

	# Debug: print( joy_xpos, joy_ypos, joy_btn )
	
	# This was the Pulse reading for RadioControl  we will use the lazy approach
	#   by keeping  the RC code and converting the joy_xpos, joy_ypos to the
	#   equivalent us_speed, us_dir
	#
	# us_speed  = time_pulse_us( ch_speed, 1 )
	# us_dir = time_pulse_us( ch_dir, 1 )
	us_speed = map( joy_ypos, 0, 65535, SPEED_CENTER_US+RANGE_US, SPEED_CENTER_US-RANGE_US )# Equiv 1934 uSec, 1035 usec
	us_dir = map( joy_xpos, 0, 65535, DIR_CENTER_US+RANGE_US, DIR_CENTER_US-RANGE_US)# Equiv 2002 uSec, 1101 uSec

	# If button press ==> Make like if we did lost communication => will stop the Zumo
	if joy_btn==1:
		us_speed = -1
		us_dir = -1

	# Original code for the RC time_pulse_us based control
	if (us_speed < 0) or (us_dir < 0):
		z.motors.stop()
		z.led.toggle()
		# no need to sleep, time_pulse_us timeout
		# will insert the required delay in the execution.
		continue

	# uSec --> -400 to +400
	speed = map( us_speed, SPEED_CENTER_US-RANGE_US, SPEED_CENTER_US+RANGE_US, +300, -300 )
	dir_diff = map( us_dir, DIR_CENTER_US+RANGE_US, DIR_CENTER_US-RANGE_US, -100, +100 )

	# print( speed, dir_diff )
	if abs(speed)<=25:
		speed = 0
	if abs(dir_diff)<=10:
		dir_diff = 0
	if speed<=-25:
		dir_diff *= -1
	elif speed==0:
		dir_diff *= 2
	speed_left = int(speed + dir_diff)
	speed_right = int(speed - dir_diff)
	if speed_left<-400:
		speed_left = -400
	if speed_left>400:
		speed_left = 400
	if speed_right<-400:
		speed_right=-400
	if speed_right>400:
		speed_right=400
	#print( us_speed," ", us_dir, " | ",  speed_left, " ", speed_right )
	z.motors.setSpeeds( speed_left, speed_right )
	time.sleep_ms(100)
