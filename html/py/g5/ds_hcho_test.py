#-*- coding:UTF-8 -*-
import serial
import time
import datetime
import struct
import sys  
sys.path.append('../')


DeviceID = 353442
HCHO_SenorID = 399191
REQ_READ_HCHO = "\x42\x4d\x01\x00\x00\x00\x90"

class mhz19():
    timeout = 2
    last_HCHO = 0
    
    def logout(self, str):
        print "%s %s"%(datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3], str)
        sys.stdout.flush()

    class TCommunicationError(Exception):
        pass

    def __init__(self):
        #super(mhz19, self).__init__()
        self.ser = None

    def Send(self):
        if self.ser:
           self.ser.close()
        self.ser = serial.Serial("/dev/ttyUSB1", 9600, timeout = 3)
        self.ser.write(REQ_READ_HCHO)
        self.logout("send")
    
    def GetData(self):
        resp_len = 10
        starttime = time.time()
        self.Send()
        
        while True:
            mytime = time.time()
            if mytime - starttime > self.timeout:
                self.logout("wait DS_HCHO data timeout")
                starttime = time.time()
                self.Send()
                #return []
            
            # 获得接收缓冲区字符
            ##time.sleep(0.05)
            count = self.ser.inWaiting()
            #print "read:"+str(count)
            if count >= resp_len:
                resp = self.ser.read(resp_len)
                self.ser.flushInput()
                recv_hex=resp.encode('hex')
                self.logout( recv_hex)
                
                payload = [ord(x) for x in resp[0:-2]]
                crchl = sum(payload) & 0xFFFF
                crch = crchl >> 8 & 0xFF
                crcl = crchl & 0xFF
                can_send = False

                if crch != ord(resp[-2]) or crcl != ord(resp[-1]):
                    #校验错误, 重新发送数据
                    pass                    
                else:
                    #注意数据平滑和无效数据
                    hcho_ug = (1000 * (payload[6] * 256 + payload[7])/(pow(10, (payload[5]-1))))
                    self.logout("hcho = " + str(hcho_ug) + "ug/m3")
                    
                    if hcho_ug >= 0:
                        can_send = (self.last_HCHO == 0 or hcho_ug < 3*self.last_HCHO)
                        self.last_HCHO = hcho_ug

                if can_send:
                    pass
                    '''
                    return [{
                                "name": "HCHO",
                                "symbol": "ug/m3",
                                "device": DeviceID,
                                "sensor": HCHO_SenorID,
                                "data": hcho_ug
                            }]
                    '''
                #else:
                    #time.sleep(0.1)
                    #self.Send()
        
            time.sleep(0.01)
        
if __name__ == '__main__':
    sensor = mhz19()
    print sensor.GetData()
