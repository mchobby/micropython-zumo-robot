"""
main.py - the minimalist main.py - just avoids the motors to starts.

* Author(s):  Meurisse D. from MCHobby (shop.mchobby.be).

See project source @ https://github.com/mchobby/micropython-zumo-robot
REQUIRES library zumoshield.py in the project source
"""

from zumoshield import ZumoShield
from machine import Pin

z = ZumoShield() # will stop the motors

# Light Up the MicroControler onbloard LED
z.mcu_led.on()
