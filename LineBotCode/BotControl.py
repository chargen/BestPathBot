#!/usr/bin/env python

import sys, getopt, socket, time, random
from BrickPi import *

BrickPiSetup()

Brick_Pi_Port = PORT_4
BrickPi.MotorEnable[PORT_B] = 1 #right motor
BrickPi.MotorEnable[PORT_C] = 1 #left motor
BrickPi.SensorType[Brick_Pi_Port] = TYPE_SENSOR_EV3_COLOR_M0
BrickPiSetupSensors()
##global variables


class botClient(object):
    DEFAULT = 65 #default color
    MULTIPLIER = 1
    background = DEFAULT
    ERROR = 3 #margin of error
    color = DEFAULT #starting color
    min_color = color
    badPath = 25 #bad path color I switched these values since green read as 13 or lower
    goodPath = 12
    full = 100
    stop = 0
    creep = 50
    call_count = 2

    def _init_(self):
        self.move()

    def move(self, motor, turn):
        if(turn):
            time.sleep(.1)
            BrickPi.MotorSpeed[PORT_B] = -motor
            BrickPi.MotorSpeed[PORT_C] = motor
        else:
            BrickPi.MotorSpeed[PORT_B] = motor
            BrickPi.MotorSpeed[PORT_C] = motor

    #reads in a random value from 0 - 100
    def read_color(self):
        temp = BrickPi.Sensor[Brick_Pi_Port]
        while (temp > 100 or temp < 1):
            BrickPiUpdateValues()
            temp = BrickPi.Sensor[Brick_Pi_Port]
        return temp
    
    #Adjust for background discrepancy
    def adjust_bg(self):
        count = 0
        self.move(0, 0)
        time.sleep(1)
        while(count < 200):
            BrickPiUpdateValues()
            time.sleep(.01)
            temp_col = self.read_color()
            if temp_col > (self.DEFAULT + self.ERROR) or temp_col < (self.DEFAULT - self.ERROR):
                if temp_col < 100 and temp_col > 1:
                    self.background = temp_col
            else:
                self.background = self.DEFAULT

            count = count + 1
        time.sleep(1)
        print "Background Color is: ", self.background

    def check_encounter(self): #determines whether or not a line has been encountered
        BrickPiUpdateValues()
        if int(BrickPi.Sensor[Brick_Pi_Port]) < 100 and int(BrickPi.Sensor[Brick_Pi_Port]) > 1:
            self.color = self.read_color()
            if self.color < (self.background - self.ERROR): #if read color falls below default white
                count = 0
                while count < 200:
                    BrickPiUpdateValues()
                    self.move(0,0)
                    count = count + 1
                    self.min_color = self.read_color()
                if self.color < self.min_color: 
                    self.min_color = self.color
                    return 1
                elif self.color > self.min_color and self.color < self.background:
                    self.color = self.min_color
                    return 1
                else: return 0
            else: return 0
        else: return 0

    def check_path_end(self):
        print "Check#: ", (3 - self.call_count)
        if self.call_count < 1:
            self.move(0, 0)
            self.call_count = 3
        self.call_count = self.call_count - 1
            
        temp = self.read_color()
        count = 0
        while count < 20:
            BrickPiUpdateValues()
            self.move(self.creep,0)
            count = count + 1
        count = 0
        if temp >= (self.badPath - self.ERROR) and temp <= (self.badPath + self.ERROR):
            while count < 200:
                BrickPiUpdateValues()
                count = count + 1
                temp = self.read_color()
            if temp < (self.badPath - self.ERROR) or temp > (self.badPath + self.ERROR):
                return 2
            print "Bad path found"
            return 0
        if temp >= (self.goodPath - self.ERROR) and temp <= (self.goodPath + self.ERROR):
            while count < 200:
                BrickPiUpdateValues()
                count = count + 1
                temp = self.read_color()
            if temp < (self.goodPath - self.ERROR) or temp > (self.goodPath + self.ERROR):
                return 2
            print "Good path found"
            return 1
        return 2 #return arbitrary value for neither case being true


    def start(self):
        self.move(100, 0)
        count = 0
        print "Initial Check: ", self.color
        if self.check_encounter():
            print "Second Check: ", self.color
            while count < 100:
                BrickPiUpdateValues()
                self.move(-50, 0)
                count = count + 1
            return 1

    def get_color(self):
        return self.color

    def follow_line(self):
        self.move(50, 0)
        print "Following Line"
        pathend = 2
        while(pathend > 1):
            BrickPiUpdateValues()
            pathend = self.check_path_end()
            temp = self.read_color()
            BrickPi.MotorSpeed[PORT_B] = int(((self.background - self.read_color()) * self.MULTIPLIER))
            BrickPi.MotorSpeed[PORT_C] = int(((self.read_color() - self.min_color) * self.MULTIPLIER))
        return pathend

    ## Robot behavior if bad line encountered
    ## Bot will slowly spiral outward until a line is encountered
    def wander(self):
        count = 0
        while(count < 20):
            BrickPiUpdateValues()
            self.move(-20, 0);
            count = count + 1
        count = 0
        while not self.check_encounter():
            BrickPiUpdateValues()
            BrickPi.MotorSpeed[PORT_B] = self.creep - count
            BrickPi.MotorSpeed[PORT_C] = self.creep
            if count > (self.ERROR): #arbitrary value to keep motor speed from ever truly being equal
                count = count - 1
            time.sleep(.2)
        self.move(0, 0)


    def turn(self):
        counter = 0
        while (counter < 500):
            BrickPiUpdateValues()
            if (int(BrickPi.Sensor[Brick_Pi_Port]) <= 100 and int(BrickPi.Sensor[Brick_Pi_Port]) > 1):
                if (BrickPi.SensorType[Brick_Pi_Port] <= 65):
                    BrickPi.MotorSpeed[PORT_B] = -50
                    BrickPi.MotorSpeed[PORT_C] = 50
            counter = counter + 1


def main(argv):
    TCP_IP = '127.0.0.1'
    TCP_PORT = 5005
    BUFFER_SIZE = 1024

    myBot = botClient()

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

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TCP_IP, TCP_PORT))

    #run loop
    run = 1
    myBot.adjust_bg()
    while(run):
        BrickPiUpdateValues()

        if myBot.start():
            s.send("C") #notify server color incoming
            data = s.recv(BUFFER_SIZE) #check server readiness
            if data == "R":
                print "Ready"
                data = None
                s.send(str(int(myBot.get_color()))) #send encountered color
                print "Color sent to server for verification..."
                data = s.recv(BUFFER_SIZE)#check if color has been encountered before or not
                if data == "E": #enter if path has been encountered
                    data = None
                    data = int(float(s.recv(BUFFER_SIZE))) #if encountered receive path ranking
                    myBot.move(0, 0)
                    if data: #enter if path is good
                        data = None
                        data = int(float(s.recv(BUFFER_SIZE))) #receive best path
                        print "Best path found: ", data
                        data = None
                        myBot.follow_line()
                        run = 0 ##exit while loop
                while data == "N": #enter if path not encountered
                    myBot.turn()
                    BrickPiUpdateValues()
                    pathrank = myBot.follow_line() #check if robot has reached the end of the path
                    if pathrank == 1: #enter if path is good
                        s.send("G") #send good to server
                        run = 0 ##exit while loop
                        data = None
                    elif pathrank == 0: #enter if path is bad
                        s.send("B") #send bad to server
                        data = None
                        myBot.wander()

        if not run:
            print "Done"
        data = None

    s.close()


if __name__ == "__main__":
    main(sys.argv[1:])
