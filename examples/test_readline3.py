""" test_readline3.py - Stress test version of Line Reading using using ZumoShield class.
						reload calibration data to avoids calibrate operation

See project source @ https://github.com/mchobby/micropython-zumo-robot

27 may 2022 - domeu - initial test for Pico
"""
# Arrêter les moteurs
from zumoshield import ZumoShield
import time
z = ZumoShield()

z.play_2tones()
z.button.waitForButton()

# Reload calibration data
z.ir.calibrationOn.load_json( '{"maximum": [2000, 1775, 1475, 1172, 1500, 2000], "minimum": [303, 303, 303, 303, 303, 304], "initialized": true}' )
z.ir.calibrationOff.load_json( '{"maximum": null, "minimum": null, "initialized": false}' )

counter = 0
print("Move the Zumo over the line to read line position.")
while True:
	# With the Zumo blade going forward
	#   Value from 500 to 4500 : line is placed from left to right
	#   value 2500 : line centered on the zumo
	#   value 0 : line exceed on the left
	#   value 5000 : line exceed on the right
	position = z.ir.readLineBlack()
	counter += 1
	if (counter % 100)==0:
		print( '%6i: Line position: %i' % (counter,position) )
	if (counter % 1000)==0:
		z.play_blip()
