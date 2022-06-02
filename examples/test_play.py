""" test_play.py - just play a note

See project source @ https://github.com/mchobby/micropython-zumo-robot

23 jul 2021 - domeu - initial writing
"""
from zumoshield import ZumoShield
import time
zumo = ZumoShield()
print( "Play arbitrary string" )
zumo.buzzer.play(">g32>>c32")
time.sleep(2)

print( "Play blip" )
zumo.play_blip()
time.sleep(2)

print( "play 2tones" )
zumo.play_2tones()
time.sleep(2)

print( "play done" )
zumo.play_done()

print( "That s all Folks")
