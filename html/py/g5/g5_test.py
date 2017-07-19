#-*- coding:UTF-8 -*-
import serial
import time
import struct
import sys  
sys.path.append('../')


DeviceID = 353442
PM2_5_SenorID = 398519
PM10_SenorID = 398528

class g5():
    def __init__(self):
        #super(PMS5003, self).__init__()
        self.ser = serial.Serial("/dev/ttyUSB0", 9600)

    def GetData(self):
        index = 0
        buff_size = 0
        buff = b''
        
        while True:
            # 获得接收缓冲区字符
            count = self.ser.inWaiting()
            #print "read:"+str(count)

            recv = self.ser.read(count)
            self.ser.flushInput()
            recv_hex=recv.encode('hex')
            #print recv_hex
            buff += recv
            buff_size = len(buff)
            #print "buff_size="+str(buff_size)+" index="+str(index)
            while buff_size - index > 1:
                sign1,sign2 = struct.unpack(">bb", buff[index:index+2])
                
                if sign1 == 0x42 and sign2 == 0x4d:
                    #print "find head, index=" + str(index) + " buff_size="+str(buff_size)
                    #长度足够的话>=32
                    if buff_size - index >= 32:
                        sign1,sign2,frame_length,pm1_0_cf,pm2_5_cf,pm10_cf,pm1_0,pm2_5,pm10,cnt_03,cnt_05,cnt_10,cnt_25,cnt_50,cnt_100,reserve,checksum = struct.unpack(">bbHHHHHHHHHHHHHHH", buff[index:index+32])
                        d1,d2,d3,d4,d5,d6,d7,d8,d9,d10,d11,d12,d13 = struct.unpack(">xxxxxBxBxBxBxBxBxBxBxBxBxBxBxBxx", buff[index:index+32])
                        print time.strftime("%H:%M:%S", time.localtime()) +  "pm1.0 pm2.5 pm10="+str(pm1_0)+" "+str(pm2_5)+" "+str(pm10);

                        #前边的数据都可以抛弃了
                        buff = buff[index + 32:]
                        buff_size = len(buff)
                        index = 0
                    else:
                        #找到head，但长度不够
                        break
                else:
                    index = index + 1
                
            #print index
            time.sleep(0.1)
            
        return [{
                    "name": "PM2.5",
                    "symbol": "ug/m^3",
                    "device": DeviceID,
                    "sensor": PM2_5_SenorID,
                    "data": pm2_5
                },
                {
                    "name": "PM10",
                    "symbol": "ug/m^3",
                    "device": DeviceID,
                    "sensor": PM10_SenorID,
                    "data": pm10
                }]
if __name__ == '__main__':
    sensor = g5()
    print sensor.GetData()
