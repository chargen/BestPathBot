#!/usr/bin/env python

import sys, getopt, socket, time, random

class botClient(object):
    DEFAULT = 90 #default color
    ERROR = 3 #margin of error
    color = DEFAULT #starting color
    badPath = 7 #bad path color
    goodPath = 10

    def _init_(self):
        time.sleep(5)
        self.move()

    def move(self):
        print "Proceeding forward"
        time.sleep(5)

    #reads in a random value from 0 - 100
    def read_color(self):
        return random.random() * 100

    def check_encounter(self): #randomly determines whether or not a line has been encountered
        prv_col = self.color
        if (random.random() > 0.7):
            self.color = self.read_color()
            if self.color < (self.DEFAULT - self.ERROR): #if read color falls below default white
                print "Previous Color: ", prv_col, "| Line encountered: ", self.color
                return 1
            else: return 0
        else:
            print "No line encountered"
            return 0

    def check_path_end(self):
        temp = self.read_color()
        if temp >= (self.badPath - self.ERROR) and temp <= (self.badPath + self.ERROR):
            print "Bad path found"
            return 0
        if temp >= (self.goodPath - self.ERROR) and temp <= (self.goodPath + self.ERROR):
            print "Good path found"
            return 1


    def start(self):
        print "Initial Check: "
        if self.check_encounter():
            time.sleep(1)
            print "Second Check: ", self.color
            return 1

    def get_color(self):
        return self.color

    def follow_line(self):
        self.move()
        print "Following Line"



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
    while(run):

        if myBot.start():
            myBot.move()
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
                    if data: #enter if path is good
                        data = None
                        data = int(float(s.recv(BUFFER_SIZE))) #receive best path
                        print "Best path found: ", data
                        data = None
                        myBot.follow_line()
                        run = 0 ##exit while loop
                while data == "N": #enter if path not encountered
                    myBot.follow_line()
                    time.sleep(2)
                    check = myBot.check_path_end() #check if robot has reached the end of the path
                    if check == 1: #enter if path is good
                        s.send("G") #send good to server
                        run = 0 ##exit while loop
                        data = None
                    elif check == 0: #enter if path is bad
                        s.send("B") #send bad to server
                        data = None

        if not run:
            print "Done"
        data = None

    s.close()


if __name__ == "__main__":
    main(sys.argv[1:])
