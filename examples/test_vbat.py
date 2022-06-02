""" test_vbat.py - Read the Zumo battery voltage.

    J9 MUST BE CLOSED ON THE ZUMO BOARD to get voltage battery

See project source @ https://github.com/mchobby/pyboard-driver/tree/master/zumo-robot

18 may 2022 - domeu - initial writing
"""

from machine import Pin, ADC

# Resitor Voltage Divider
# Ideal divider is 20K + 20K
R_DIVIDER = 2

# R Divider can be recalculated - does not offer best accuracy
#   probably because of DC/DC regulator internal & battery internal resistor)
# Measure resistance between GP28 to VIN => RVin = 12.90 KOhms
# Measure resistance between FP28 to GND => RGnd = 10.68 KOhms
# R_DIVIDER = (RGnd + RVin ) / RGnd = (10.68 + 12.90) / 10.68 = 2.20

adc = ADC( Pin(28) )
# Mean reading
vadc_sum = 0
for i in range( 10 ):
	val = adc.read_u16() # 0..65535
	vadc = 3.3 * val / 65535 # Volts on ADC pin
	vadc_sum += vadc
vadc = vadc_sum / 10
vbat = vadc * R_DIVIDER
print( 'ADC Voltage is %f' % vadc )
print( 'Battery voltage is %f' % vbat )
