#-*- coding:UTF-8 -*-
import serial
import time
import struct
import sys  
sys.path.append('../')


DeviceID = 353442
CO2_SenorID = 398614
REQ_READ_CONCENTRATION = "\xFF\x01\x86\x00\x00\x00\x00\x00\x79"

class mhz19():
    timeout = 5
    last_CO2 = 0
    
    def logout(self, str):
        print "%s %s"%(time.strftime("%m-%d %H:%M:%S"), str)
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
        self.ser.write(REQ_READ_CONCENTRATION)
    
    def GetData(self):
        resp_len = 9
        starttime = time.time()
        self.Send()
        
        while True:
            mytime = time.time()
            if mytime - starttime > self.timeout:
                #self.logout("wait MHZ19 data timeout")
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
                #print recv_hex
                
                payload = [ord(x) for x in resp[1:-1]]
                crc16 =((sum(payload) % 256) ^ 0xFF) + 1
                can_send = False

                if crc16 != ord(resp[-1]):
                    #校验错误, 重新发送数据
                    pass                    
                else:
                    #注意数据平滑和无效数据
                    co2_ppm = payload[1] * 256 + payload[2]
                    self.logout("co2 = " + str(co2_ppm) + "ppm")
                    
                    if co2_ppm >= 0:
                        can_send = (self.last_CO2 == 0 or co2_ppm < 3*self.last_CO2)
                        self.last_CO2 = co2_ppm

                if can_send:
                    pass
                    '''
                    return [{
                                "name": "CO2",
                                "symbol": "ppm",
                                "device": DeviceID,
                                "sensor": CO2_SenorID,
                                "data": co2_ppm
                            }]
                    '''
                #else:
                    #time.sleep(0.1)
                    #self.Send()
        
            time.sleep(0.1)
        
if __name__ == '__main__':
    sensor = mhz19()
    print sensor.GetData()
