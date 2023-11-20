""" RFM69 RC Zumo : Emitter - joystick remote control

Emit RC remote control messages through RFM69HCW SPI module - RC EMITTER node
Must be tested togheter with rfm_rc_joy_rx.py or rfm_rc_zumo.py

See GitHub : https://github.com/mchobby/micropython-zumo-robot/tree/main/extras/RFM69

RFM69HCW breakout : https://shop.mchobby.be/product.php?id_product=1390
RFM69HCW breakout : https://www.adafruit.com/product/3071
"""

from machine import SPI, Pin, ADC, Signal
from rfm69 import RFM69
import time

FREQ           = 433.1
ENCRYPTION_KEY = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
NODE_ID        = 120 # ID of this node
RECEIVER_ID    = 100 # ID of the node (Receiver) to be contacted

# Joystick interface
xpos = ADC(Pin(27))
ypos = ADC(Pin(26))
btn = Signal( Pin(21, Pin.IN, Pin.PULL_UP), invert=True )

# RFM69 interface
spi = SPI(0, miso=Pin(4), mosi=Pin(7), sck=Pin(6), baudrate=50000, polarity=0, phase=0, firstbit=SPI.MSB)
nss = Pin( 5, Pin.OUT, value=True )
rst = Pin( 22, Pin.OUT, value=False )

rfm = RFM69( spi=spi, nss=nss, reset=rst )
rfm.frequency_mhz = FREQ

# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm.encryption_key = ( ENCRYPTION_KEY )
rfm.node    = NODE_ID # This instance is the node 120

print( 'Freq         :', rfm.frequency_mhz )
print( 'NODE         :', rfm.node )
print( 'Receiver NODE:', RECEIVER_ID )

# Send a packet and waits for its ACK.
# Note you can only send a packet up to 60 bytes in length.
counter = 1
rfm.destination = RECEIVER_ID # Send to specific node 100
while True:
	msg = "%s,%s,%s" % (xpos.read_u16(),ypos.read_u16(),btn.value() )
	ack = rfm.send(  msg.encode("ASCII") )
	#print( "sent", counter, msg)
	counter += 1
	time.sleep(0.1)
