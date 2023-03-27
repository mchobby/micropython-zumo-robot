""" test_readline1.py - a version Line Reading using using ZumoShield class.

See project source @ https://github.com/mchobby/micropython-zumo-robot

18 may 2022 - domeu - initial test for Pico
"""
# Arrêter les moteurs
from zumoshield import ZumoShield
import time
zumo = ZumoShield()

print("Move the Zumo over the line while calibrating (in 10 steps).")
print("  This will helps to identifies the white/black contrast.")
#
for i in range(10):
	zumo.ir.calibrate()
	time.sleep(0.5)

print("")
print("")
print("")
print("Read the line position")
print("")
while True:
	# With the Zumo blade going forward
	#   Value from 500 to 4500 : line is placed from left to right
	#   value 2500 : line centered on the zumo
	#   value 0 : line exceed on the left
	#   value 5000 : line exceed on the right
	position = zumo.ir.readLineBlack()
	print( 'Line position: ', position )
	time.sleep( 1 )
