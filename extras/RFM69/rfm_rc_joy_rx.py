""" RFM69 RC Zumo : RECEIVER - read messages sends by rfm_rc_joy.py
    This script is designed for debugging purpose

Receives message over RFM69HCW SPI module - RC RECEIVER node
Must be tested togheter with rfm_rc_joy.py

See GitHub : https://github.com/mchobby/micropython-zumo-robot/tree/main/extras/RFM69

RFM69HCW breakout : https://shop.mchobby.be/product.php?id_product=1390
RFM69HCW breakout : https://www.adafruit.com/product/3071
"""

from machine import SPI, Pin
from rfm69 import RFM69
import time

FREQ           = 433.1
ENCRYPTION_KEY = b"\x01\x02\x03\x04\x05\x06\x07\x08\x01\x02\x03\x04\x05\x06\x07\x08"
NODE_ID        = 100 # ID of this my node node

spi = SPI(0, miso=Pin(4), mosi=Pin(7), sck=Pin(6), polarity=0, phase=0, firstbit=SPI.MSB) # baudrate=50000,
nss = Pin( 5, Pin.OUT, value=True )
rst = Pin( 22, Pin.OUT, value=False )

rfm = RFM69( spi=spi, nss=nss, reset=rst )
rfm.frequency_mhz = FREQ

# Optionally set an encryption key (16 byte AES key). MUST match both
# on the transmitter and receiver (or be set to None to disable/the default).
rfm.encryption_key = ( ENCRYPTION_KEY )
rfm.node = NODE_ID # This instance is the node 123

print( 'Freq            :', rfm.frequency_mhz )
print( 'NODE            :', rfm.node )

print("Waiting for packets...")
while True:
	packet = rfm.receive( with_ack=True )
	# Optionally change the receive timeout from its default of 0.5 seconds:
	# packet = rfm.receive(timeout=5.0)
	# If no packet was received during the timeout then None is returned.
	if packet is None:
		# Packet has not been received
		pass
	else:
		# Received a packet!
		print( "Received (raw bytes):", packet )
		# And decode to ASCII text
		packet_text = str(packet, "ascii")
		print("Received (ASCII):", packet_text)
		print("-"*40)
