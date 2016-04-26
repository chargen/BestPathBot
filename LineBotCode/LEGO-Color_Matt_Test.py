#!/usr/bin/env python
# Jaikrishna
# Initial Date: June 24, 2013
# Last Updated: Oct 21, 2014 by John
#
# These files have been made available online through a Creative Commons Attribution-ShareAlike 3.0  license.
# (http://creativecommons.org/licenses/by-sa/3.0/)
#
# http://www.dexterindustries.com/
# This code is for testing the BrickPi with a Lego Color Sensor

from BrickPi import *   #import BrickPi.py file to use BrickPi operations

BrickPiSetup()  # setup the serial port for communication

BrickPi.MotorEnable[PORT_B] = 1 #Enable the Motor A
BrickPi.MotorEnable[PORT_C] = 1

Brick_Pi_Port = PORT_4										# Setup the sensor on Port 1.
BrickPi.SensorType[Brick_Pi_Port] = TYPE_SENSOR_EV3_COLOR_M0    #Set the type of sensor 


BrickPiSetupSensors()   #Send the properties of sensors to BrickPi

power = 25

BrickPi.MotorSpeed[PORT_B] = power 
BrickPi.MotorSpeed[PORT_C] = power

while True:
    stop = 0
    brickPiValue = 0
    result = BrickPiUpdateValues()  # Ask BrickPi to update values for sensors/motors
    if (int(BrickPi.Sensor[Brick_Pi_Port]) <= 100 and int(BrickPi.Sensor[Brick_Pi_Port]) > 1):
        brickPiValue = BrickPi.Sensor[Brick_Pi_Port]
        print brickPiValue #BrickPi.Sensor[PORT] stores the value obtained from sensor
        if (brickPiValue <= 65):
            BrickPi.MotorSpeed[PORT_B] = -power
            BrickPi.MotorSpeed[PORT_C] = power
        else:
            BrickPi.MotorSpeed[PORT_B] = power
            BrickPi.MotorSpeed[PORT_C] = power
    time.sleep(.1)     # sleep for 100 ms
    
