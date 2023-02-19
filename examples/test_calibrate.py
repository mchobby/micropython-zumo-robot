""" test_calibrate.py - perform a calibration process and return data as json string.
                        this allow to reload the calibration data without running a calibration process.

See project source @ https://github.com/mchobby/pyboard-driver/tree/master/zumo-robot

19 feb 2022 - domeu - initial writing
"""

from zumoshield import *
z = ZumoShield()

print( "Press user button to start calibration." )
z.play_blip()
z.button.waitForButton()

 z.ir_calibration()
z.play_blip()

# Getting calibration data as string
json_on = z.ir.calibrationOn.as_json()
json_off = z.ir.calibrationOff.as_json()
print( "calibrationOn : %s" % json_on )
print( "calibrationOff : %s" % json_off )

# --------------------------------------------------------
# Example of calibration reloading (from string ressource)
# --------------------------------------------------------

# json_on = '{"maximum": [2000, 1775, 1475, 1172, 1500, 2000], "minimum": [303, 303, 303, 303, 303, 304], "initialized": true}'
# json_off = '{"maximum": null, "minimum": null, "initialized": false}'
# z.ir.calibrationOn.load_json( json_on )
# z.ir.calibrationOff.load_json( json_off )
# # Print config back to ensure that data have been properly reloaded.
# print( z.ir.calibrationOn.as_json() )
# print( z.ir.calibrationOff.as_json() )
