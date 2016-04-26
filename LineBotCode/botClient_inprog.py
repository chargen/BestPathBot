#!/usr/bin/env python

import sys, getopt, socket
from BrickPi import *

BrickPiSetup()

BrickPi.MotorEnable[PORT_B] = 1
BrickPi.MotorEnable[PORT_C] = 1
BrickPi.SensorType[PORT_1] = TYPE_SENSOR_EV3_COLOR_M2
BrickPiSetupSensors()

class botClient():
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 1024

    full = 200
    stop = 0
    creep = 50
    current_line = []
    current_line.append([])
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    stop_color = 255

    def __init__():
        power = full_power
        BrickPi.MotorSpeed[PORT_B] = power
        BrickPi.MotorSpeed[PORT_C] = power
        try:
            opts, args = getopt.getopt(argv, "ha:p:", ["addr=", "port="])
        except getopt.GetoptError:
            print 'botClient.py -a <serverip> -p <port>'
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print 'botClient.py -a <serverip> -p <port>'
                sys.exit()
            elif opt in ("-s", "--addr"):
                TCP_IP = arg
            elif opt in ("-p", "--port"):
                TCP_PORT = int(arg)
        print 'Server IP is: ', TCP_IP
        print 'Server PORT is: ', TCP_PORT

        s.connect((TCP_IP, TCP_PORT))
        run()

    def run():
        while(True):
            set_motor_power(full,full)
        s.close()

    def set_motor_power(self, powerB, powerC):
        BrickPi.MotorSpeed[PORT_B] = powerB
        BrickPi.MotorSpeed[PORT_C] = powerC

    def line_encountered(self, color):
        color_encountered = color
        peak_color = color #maximum color value
        current_line[0].extend(color) #add minimum color value to data array
        if (color > 0): #need to figure out actual value of white also needs to be a range
            set_motor_power(self, stop, stop)
            while (color <= color_encountered)
                if ((color = BrickPiUpdateValues()) != 0):#again following the *false* assumption that white = 0
                    set_motor_power(creep, creep)
                    if (color > peak_color):
                        peak_color = color
                else:
                    set_motor_power(-creep, -creep)
                    if (color > peak_color):
                        peak_color = color
            current_line[0].extend(peak_color) #add maximum color value to data array

    def follow_line(self, peak_color, mult):
        bool left = False
        if (random.random() > 0.5 )
            left = True
        while(color = BrickPiUpdateValues() != stop_color):
            if(left)
                set_motor_power(((0 - color) * mult), ((peak_color - color) * mult))
            else
                set_motor_power(((peak_color - color) * mult), ((0 - color) * mult))


def main(argv):
    myBot = botClient()
    myBot.init()
    wait(3000)
    myBot.run()


if __name__ == "__main__":
    main(sys.argv[1:])
