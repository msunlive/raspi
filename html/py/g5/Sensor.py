#-*- coding:UTF-8 -*-
import serial
import time
import datetime
import random
import struct
import sys  
import os

class Sensor(object):
    timeout = 2
    timeout_count = 0
    
    right_port = -1
    try_port = -1
    total_port = 5

    def __init__(self):
        super(Sensor, self).__init__()

    def GetValue():
        return 0
        
    def logout(self, str):
        print "%s %s"%(datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3], str)
        sys.stdout.flush()
        
    def getUSBPort(self):
        p = 0
        if self.right_port >= 0:
            p = self.right_port
        else:
            #当前port是否可用
            self.getNext()
            while not self.isUSBOK(self.try_port):
                self.getNext()
            p = self.try_port
            print "try: " + self.__class__.__name__ + " " + str(p)               
        
        return "/dev/ttyUSB" + str(p)
        
    def getNext(self):
        if self.try_port < 0:
            self.try_port = random.randint(0, self.total_port - 1)
        else:
            self.try_port = (self.try_port + 1) % self.total_port
        
    def isUSBOK(self, port):
        has_usb = os.path.exists("/dev/ttyUSB" + str(port))
        return has_usb
        
    def gotRightData(self, ok = True):
        if not ok:
            self.right_port = -1
        else:
            self.timeout_count = 0
            if self.right_port != self.try_port:
                self.right_port = self.try_port
                self.logout("got right data: "  + self.__class__.__name__ + " @ " + str(self.right_port))
        
    def isReady(self):
        return self.right_port >= 0
        
    def waitDataTimeout(self):
        #超时次数超过3也要重新寻找端口
        self.timeout_count += 1
        print self.__class__.__name__ + " timeout " + str(self.timeout_count)
        if self.timeout_count > 3:
            self.gotRightData(False)