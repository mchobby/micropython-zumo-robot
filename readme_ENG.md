[Ce fichier existe également en FRANCAIS ici](readme.md)

# ROBOT ZUMO V1.3 under MicroPython with the Pyboard or the Pico

This MicroPython portage is about the [Zumo Robot from Pololu](https://www.pololu.com/product/2510). That robot can be assembled from various parts or you can be purchased fully assembled (like shown on the picture). This robot is designed for Arduino Uno board __BUT WE WILL MAKE IT RUNNING__ with a __MicroPython Pyboard__ or a __Raspberry-Pi Pico__.

The Zumo robot is composed of a chassis, two DC motor, a shield interface for Arduino, a front blade used to push objects or others robots in the neighbour and infrared reflectance sensor array used to follow lines.

For more details about the Zumo robot, you can browse the [Zumo Robot page @ MCHobby](https://shop.mchobby.be/fr/prototypage-robotique-roue/448-robot-zumo-pour-arduino-assemble-moteurs-3232100004481-pololu.html) or the [Zumo Robot @ Pololu](https://www.pololu.com/product/2510)

![ROBOT ZUMO under MicroPython](docs/_static/robot-zumo-micropython.jpg)

Initialy, this robot is designed for Arduino Uno / Leonardo board.
In this project the Zumo robot can be programmed with:
* An  [adaptateur Pyboard vers Zumo](https://shop.mchobby.be/product.php?id_product=2040)
* d'un [Adaptateur Pico vers Zumo](https://shop.mchobby.be/product.php?id_product=2430)

All the library and examples made by [Pololu](https://www.pololu.com/) have been ported to  Micropython.

# Configure your Zumo
For optimal usage of your Zumo Robot with this libraryn we do recommand the following hardware configuration.

## Buzzer
Place the buzzer jumper to select the 328p option.

## Line follower
Flip over your Zumo and gently remove the line follower array from its socket.

Place the LED ON jumper on the position labelled 2. Then put back the line follower array in place.

## Battery voltage (optional)
__<<< PICO implementation only >>>__

If you want to read the battery voltage then solder a pinHeader (2 pins) on the ___A1___ and ___Battery Level___ location.

Next, place the jumper over the the connector.

# Wiring

## Raspberry-Pi Pico to Zumo adapter

![ROBOT ZUMO under MicroPython with Raspberry-Pi Pico](docs/_static/robotzumo-pico.jpg)

The [Pico-Zumo](https://shop.mchobby.be/product.php?id_product=2430) adapter do allow the usage of the Raspberry-Pi Pico to run the Pololu's Zumo Robot.

![ROBOT ZUMO](docs/_static/pico-zumo.jpg)

The Pico-Zumo adapter do also offers:
* Add a Pico Reset button
* Replication of the Zumo user button
* A UEXT connector (IDC 10 pins, 2.54mm) with:
 * 3.3V Power
 * SPI(0) bus
 * I2C(0) bus
 * UART(0)
 * See the [UEXT product line @ Olimex](https://www.olimex.com/Products/Modules/) or [UEXT product line @ MCHobby](https://shop.mchobby.be/fr/138-uext) .
* The 5V regulator (optionnal) do sent 5V voltage back to the ZUMO 5V pin

__Ressources:__
* [Pico-Zumo](https://shop.mchobby.be/product.php?id_product=2430) : Product sheet with lot of useful information.
* [Adapter schematic](docs/_static/schematic-pico.jpg).

## Pyboard to Zumo adapter

![ROBOT ZUMO under MicroPython with Pyboard](docs/_static/robotzumo2.jpg)

The [Pyboard-Zumo](https://shop.mchobby.be/product.php?id_product=2040) adapter is used to connect directly the MicroPython Pyboard to the Pololu's Zumo Robot.

![Pyboard to Zumo Board](docs/_static/pyboard-zumo.jpg)

The Pyboard-Zumo adapter do also offers:
* replication of the Pyboard's Reset button
* replication of the Pyboard's user button
* two Servo-Motor connector available (GND, __7.45V__, Signal)
* two additionnal servo (if you do not use the line follower)
* A UEXT connector (IDC 10 pins, 2.54mm) with:
 * 3.3V Power
 * SPI(2) bus
 * I2C(2) bus
 * UART(1)
 * See the [UEXT product line @ Olimex](https://www.olimex.com/Products/Modules/) or [UEXT product line @ MCHobby](https://shop.mchobby.be/fr/138-uext) .
* The 5V regulator (optionnal) do sent 5V voltage back to the ZUMO 5V pin

__SERVOS POWER SUPPLY:__ the power pins on the Servo connector is linked to the VIN voltage created by the Zumo with Boost regulator. __The voltage is  7.45V__. You will have to use 8V servo motors which do not loads too much the Zumo's boost regulator (do not raise weight with them).

The [adapter schematic is available here](docs/_static/schematic.jpg)

## DIY Connections
You can also make your own connexions by using wires. It is not the most beautiful creation but it does the job.

![ROBOT ZUMO](docs/_static/robotzumo.jpg)

With DIY wiring, you will need to use a [S7V7F5 5V regulator from Pololu](https://www.pololu.com/product/2119) to generates 5V from the VIN voltage provided with Zumo batteries. Follows the [power distribution schematic](https://github.com/mchobby/pyboard-driver/blob/master/UNO-R3/docs/_static/power-distribution.jpg) from the PYBOARD-UNO-R3 project.

See the schematic of [Pyboard-to-Zumo](docs/_static/schematic.jpg) or [PYBOARD-UNO-R3 project schematic](https://github.com/mchobby/pyboard-driver/tree/master/UNO-R3) to properly wire the Pyboard pin's to the Arduino's pins.

# Libraries

The required MicroPython libraries must be copied to the MicroPython board before testing the code.

The Pololu Zumo Arduino based libraries have been ported to MicroPython. __The function names and method named are very closed from from C naming convention into the MicroPython implementation__, this will help arduino users to migrate to MicroPython.

* [zumoshield.py](lib/zumoshield.py) : drive the Zumo motors + interface to line followeer, Buzzer, Zumo button, Zumo LED, microcontroler LED and accès au I2C bus.
* [pushbutton.py](lib/pushbutton.py) : helper functions for buttons.
* [zumobuzzer.py](lib/zumobuzzer.py) : Zumo buzzer helper.
* [zumoimu.py](lib/zumoimu.py) : Inertial Measurement Unit helper (Gyroscope, Magnetometer, Accelerometer)
* [qtrsensors.py](lib/qtrsensors.py) : helper for the Pololu's line follower

Following libraries was for Zumo Robot V1.2 and are deprecated now.
* lsm303.py : Helper for the 3 axis accelerometer/magnetometer.
* L3G.py : Helpers for 3 axis gyroscope.

# Test

## Zumo  default state

When the microcontroler is turned on, all the PINs are activated as input with pull-up. This result into one (or both) of the motors starts spining.

_We do need to initialize the motor pins__ as soon as possible to avoids the zumo to start running away when testing your code.

That can be done with 2 lines of codes inserted into the `main.py` file.

``` python
from zumoshield import ZumoShield
z = ZumoShield()
```

See the [examples/main.py](examples/main.py) script wich contains the minimalist code to quickly initialize the Zumo.

## Driving the motors

Place the batteries inside the Zumo then switch the power "ON".

The rear LEDs of the Zumo do light up.

![Motors of Zumo](docs/_static/motors.jpg)

Pick up the following code in the REPL session to control the Zumo motors:

``` python
from zumoshield import ZumoShield
z=ZumoShield()
# Forward
z.motors.setSpeeds( 200, 200 ) # -400..0..400
# Stop
z.motors.setSpeeds( 0, 0 ) # -400..0..400
# backward
z.motors.setSpeeds( -100, -100 ) # -400..0..400
z.motors.setSpeeds( 0, 0 ) # -400..0..400
```

The following show example how to invert the rotation of the right motor. So the Zumo will turn right.

``` python
from zumoshield import ZumoShield
from time import sleep
z=ZumoShield()
# Forward
z.motors.setSpeeds( 100, 100 ) # -400..0..400
# Turn right
z.motors.flipRightMotor( True )
z.motors.setSpeeds( 100, 100 ) # set the rotation speed
# Wait a second
sleep( 1 )
# Switch back to forward (when mentionning the speed)
z.motors.flipRightMotor( False )
z.motors.setSpeeds( 100, 100 )
sleep( 1 )
# Stop
z.motors.setSpeeds( 0, 0 ) # -400..0..400
```

Here an another example.

``` python
from zumoshield import ZumoShield
z = ZumoShield()
z.motors.setSpeeds( 100, 100 ) # -400..0..400
z.motors.stop()
```

## Buzzer

Here some examples of code coming from [mazesolver.py](examples/mazesolver.py) and playing some notes and tunes.

The tune syntax is described in the following Pololu's document for the [Zumo32U4Buzzer::play()](https://pololu.github.io/zumo-32u4-arduino-library/class_zumo32_u4_buzzer.html) method

``` python
from zumoshield import ZumoShield
from time import sleep

z=ZumoShield()
z.buzzer.play("c8")
sleep(2)
z.buzzer.play(">g32>>c32")
sleep(2)
z.buzzer.play("l16 cdegreg4")
sleep(2)
z.buzzer.play(">>a32")
sleep(2)
z.buzzer.play(">>a32")
```
You can also play notes with `playNote()` by indicating the Note, the Duration in ms and the Volume (0-15).

The example here below comes from [borderdetect.py](examples/borderdetect.py) .

``` python
from zumoshield import ZumoShield
from zumobuzzer import NOTE_G
z = ZumoShield()

for x in range(3):
		time.sleep(1)
		# Note(octave), Durée, Volume
		z.buzzer.playNote(NOTE_G(3),200,15)
time.sleep(1)
z.buzzer.playNote(NOTE_G(4),500,15)
time.sleep(1)
```

To finish, the `ZumoShield` class do have some predefined buzzer sequences.

``` python
from zumoshield import ZumoShield
zumo = Zumoshield()
zumo.play_blip()
zumo.play_2tones()
zumo.play_done()
```

## Zumo LED

The Zumo do have an orange USER LED labelled "LED 13".

![Zumo user LED](docs/_static/LEDs.jpg)

That LED is visible on the right side of the Zumo.

``` python
from zumoshield import ZumoShield
zumo = ZumoShield()
zumo.led.on()
zumo.led.off()
```

## Zumo push button

The Zumo's push button (next to the Zumo's On/OFF switch) is wired to a microcontroler pin. The pin is tied to the ground when the button is pressed.

![Zumo button](docs/_static/zumo_button.jpg)

The Zumo button is also replicated on the adapter board.

The [pushbutton.py](lib/pushbutton.py) library do contains the `Pushbutton` class can be used to detect the button state or even advanced feature as "press and release" the button. The class is made available through the `ZumoShield` (from [lib/zumoshield.py](lib/zumoshield.py) library).

``` python
from zumoshield import ZumoShield

zumo = ZumoShield()
print( "Press and release the Zumo button" )
zumo.button.waitForButton()
print( "Done" )
```
## Line follower

The line follower placed on the front of the Zumo is used to detect the presence and position of a black or white line under the robot (15mm large line).

![line following with Zumo Robot under MicroPython](docs/_static/line-follower.jpg)

The following script do activates the Infrared lines of the Line Follower and to make multiple reads of the line position.

![position of the line](docs/_static/readLine.jpg)

The `ZumoShield` class can be used to access directly the infrared sensor.

The test code can be rewrite as follow:

``` python
# Stop the motors
from zumoshield import ZumoShield
zumo = ZumoShield()

# Calibration
for i in range(10):
	print( "Calibrate %i / 10" % (i+1) )
	zumo.ir.calibrate()
	time.sleep(0.5)

# Read line position
while True:
    sensors = [0 for i in range(6)]
    position = zumo.ir.readLine( sensors )
    print( 'Line position: ', position )
    time.sleep( 1 )
```

## Inertial Measurement Unit reading

The code inside [test_imu.py](examples/test_imy.py), available here below, just made basic reading of IMU unit.

``` python
ffrom zumoshield import ZumoShield
from zumoimu import *
import time

# Allow us to have a readable label identifying the IMU
IMU_TYPE_LSM303DLHC = 1       # LSM303DLHC accelerometer + magnetometer
IMU_TYPE_LSM303D_L3GD20H = 2  # LSM303D accelerometer + magnetometer, L3GD20H gyro
IMU_TYPE_LSM6DS33_LIS3MDL = 3 # LSM6DS33 gyro + accelerometer, LIS3MDL magnetometer

imu_type_as_text = { IMU_TYPE_LSM303DLHC : "LSM303DLHC", IMU_TYPE_LSM303D_L3GD20H : "LSM303D_L3GD20H", IMU_TYPE_LSM6DS33_LIS3MDL : "LSM6DS33_LIS3MDL" }

z = ZumoShield() # Will stop motors
print( "Zumo I2C scan:", z.i2c.scan() )

imu = ZumoIMU( z.i2c ) # Start with auto detection
print( "IMU type: %s" % imu_type_as_text[imu.imu_type] )

while True:
	imu.read()
	print( "Acc= %6i, %6i, %6i  :  Mag= %6i, %6i, %6i  :  Gyro= %6i, %6i, %6i  " % (imu.a.values+imu.m.values+imu.g.values) )
	time.sleep( 0.5 )
```

Which produce the following content:

```
MicroPython v1.18 on 2022-01-17; Raspberry Pi Pico with RP2040
Type "help()" for more information.
>>>
>>> import test_imu
Zumo I2C scan: [30, 107]
IMU type: LSM6DS33_LIS3MDL
Acc=   -127,    -42,  16583  :  Mag=  -5353,  -4654, -13695  :  Gyro=    183,   -972,   -378  
Acc=   -125,    -40,  16588  :  Mag=  -5379,  -4655, -13680  :  Gyro=    148,   -959,   -366  
Acc=   -127,    -37,  16570  :  Mag=  -5372,  -4671, -13680  :  Gyro=    165,   -965,   -373  
Acc=   -125,    -44,  16583  :  Mag=  -5366,  -4642, -13688  :  Gyro=    174,   -951,   -371  
Acc=   -113,    -41,  16590  :  Mag=  -5350,  -4678, -13636  :  Gyro=    182,   -962,   -364  
Acc=   -122,    -25,  16579  :  Mag=  -5371,  -4670, -13613  :  Gyro=    157,   -940,   -364  
Acc=   -120,    -39,  16559  :  Mag=  -5361,  -4686, -13665  :  Gyro=    166,   -953,   -365  
Acc=   -113,    -39,  16589  :  Mag=  -5346,  -4644, -13673  :  Gyro=    166,   -948,   -371  
Acc=    -90,      9,  16574  :  Mag=  -5373,  -4673, -13648  :  Gyro=    235,   -780,   -462  
Acc=    -55,     14,  16593  :  Mag=  -5405,  -4657, -13618  :  Gyro=    167,   -920,   -341  
Acc=   4955,  -1384,  21446  :  Mag=  -5759,  -4419, -13937  :  Gyro=  -9584,  -9800,  11313  
Acc=  -5509,  -1035,  23783  :  Mag=  -4170,  -4768, -12563  :  Gyro=  32766, -11453,  13894  
Acc=  10218,  12080,   2196  :  Mag=  -8195,  -7845, -11131  :  Gyro= -32766,  27757,  32766  
Acc=   -834,   -955,  18470  :  Mag=  -5214,  -5658, -13521  :  Gyro= -16310,  -5711,   4933  
Acc=   -215,     67,  16611  :  Mag=  -5362,  -5564, -13492  :  Gyro=    109,   -984,   -337  
Acc=   -111,     56,  16576  :  Mag=  -5346,  -5576, -13516  :  Gyro=    190,   -887,   -353  
Acc=   -122,     55,  16538  :  Mag=  -5331,  -5573, -13477  :  Gyro=    160,   -950,   -372  
```

Some data can be correlated with the X,Y Zumo's axis (the Z axis of the magnetometer can be ignored because of the battries metal).

![Zumo Axis](docs/_static/zumo-axis.jpg)


# Pololu's ZUMO example in MicroPython

The examples here under are ported to MicroPython from the Original Pololu code samples.

## Edge detection (TO REVIEW)

The [examples/borderdetect.py](examples/borderdetect.py) example script move the Zumo inside an area bounded with a black line and use the line follower sensor to stay into such area.

This example rely on the [qtrsensors.py](lib/qtrsensors.py) library to make the job. As black lines do reflect less light than white surface, it is how the zumo detects boundaries.

Depending on the line information, the zumo motors are controled to run forward, backward or to turn.

![Edge detection with Zumo](docs/_static/zumo_robot_ring.jpg)

## Line Follower

The [examples/line_follower.py](examples/line_follower.py) script allows the Zumo to follow a black line of 15 to 20mm large over a white background (best result for 20mm).

That examples relies on [QTRsensors](lib/qtrsensors.py) and [ZumoShield](lib/zumoshield.py) classes.

This link shows up a [YouTube video of the prototype running at the Maker Fair Paris 2019](https://youtu.be/VHN83aYCH8Q) (YouTube)

## turn_square - using the mangnetometer / compass / IMU

The [examples/turn_square.py](examples/turn_square.py) example script lead the zumo to draw squares. It is the equivalant example from [TurnWithCompass.ino](https://github.com/pololu/zumo-shield-arduino-library/blob/master/examples/TurnWithCompass/TurnWithCompass.ino) from Pololu.

![Zumo Turn Square with MicroPython](docs/_static/turn_square.jpg)

Thank to the magnetometer detecting Earth's magnetic field, the zumo can measure its rotation angle and turn with angles of 90 degrees.

This example is very interesting and explains how to:
* perform the magnetometer calibration in situation.
* transform raw magnetometer reading into rotational angle (see function `heading_degrees()` )
* how to average 10 magnetometer measurement to minimize motor magnetic interference (see function `average_heading()` )
* how to calculate angles difference between two heading_degrees read (see function `relative_heading_degrees()`)


## Maze solver (TO REVIEW)

![Maze solvering](docs/_static/maze.jpg)

The [examples/mazesolver.py](examples/mazesolver.py) example script allows the Zumo to solve maze. The script of not bug free but works well.

## Gyroscope (TO REVIEW)

The [examples/gyroscope.py](examples/gyroscope.py) example script do test the gyroscope script.

Cet exemple est n'est pas encore certifié.

# Shopping list
* [Zumo Robot pour Arduino](https://www.pololu.com/product/2510) @ MCHobby
* [Zumo Robot pour Arduino](https://shop.mchobby.be/product.php?id_product=448) @ Pololu
* [__Pico to Zumo adapter__](https://shop.mchobby.be/product.php?id_product=2430) @ MCHobby
* [__Pyboard to Zumo adapter__](https://shop.mchobby.be/product.php?id_product=2040) @ MCHobby
* [MicroPython Pyboard](https://shop.mchobby.be/product.php?id_product=570) @ MCHobby
