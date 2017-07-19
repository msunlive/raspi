#-*- coding:UTF-8 -*-
import serial
import time
import struct
import sys
import aqi
sys.path.append('../')

import Sensor

DeviceID = 353442
PM2_5_SenorID = 398519
PM2_5_AQI_SenorID = 398563
PM10_SenorID = 398528
PM10_AQI_SenorID = 398564

class PMS5003(Sensor.Sensor):
    last_PM2_5 = 0
    last_PM10 = 0

    def __init__(self):
        super(PMS5003, self).__init__()
        self.ser = None

    def GetData(self):
        if self.ser:
           self.ser.close()
        self.ser = serial.Serial(self.getUSBPort(), 9600, timeout = self.timeout)
        
        index = 0
        buff_size = 0
        buff = b''
        starttime = time.time()
        
        while True:
            mytime = time.time()
            if mytime - starttime > self.timeout:
                self.logout ("wait PMS5003 data timeout")
                return []
        
            # 获得接收缓冲区字符
            count = self.ser.inWaiting()
            recv = self.ser.read(count)
            buff += recv
            buff_size = len(buff)

            while buff_size - index > 1:
                sign1,sign2 = struct.unpack(">bb", buff[index:index+2])
                
                if sign1 == 0x42 and sign2 == 0x4d:
                    #print "find head, index=" + str(index) + " buff_size="+str(buff_size)
                    #长度足够的话>=32
                    if buff_size - index >= 32:
               
                        sign1,sign2,frame_length,pm1_0_cf,pm2_5_cf,pm10_cf,pm1_0,pm2_5,pm10,cnt_03,cnt_05,cnt_10,cnt_25,cnt_50,cnt_100,reserve,checksum = struct.unpack(">bbHHHHHHHHHHHHHHH", buff[index:index+32])
                        b1,b2,b3,b4,b5,b6,b7,b8,b9,b10,b11,b12,b13,b14,b15,b16,b17,b18,b19,b20,b21,b22,b23,b24,b25,b26,b27,b28,b29,b30,b31,b32 = struct.unpack(">BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB", buff[index:index+32])
                        
                        crchl = (b1+b2+b3+b4+b5+b6+b7+b8+b9+b10+b11+b12+b13+b14+b15+b16+b17+b18+b19+b20+b21+b22+b23+b24+b25+b26+b27+b28+b29+b30)& 0xFFFF
                        crch = crchl >> 8 & 0xFF
                        crcl = crchl & 0xFF
                        
                        if crch != b31 or crcl != b32:
                            #校验错误, 重新发送数据
                            pass                    
                        else:                        
                            self.logout(" pm1.0 = "+str(pm1_0)+  "  pm2.5 = "+str(pm2_5)+  "  pm10 = "+str(pm10))

                            #注意数据平滑和无效数据
                            if pm2_5 >= 0 and pm10 >= 0:
                                can_send = (self.last_PM2_5 == 0 or pm2_5 < 3*self.last_PM2_5) and (self.last_PM10 == 0 or pm10 < 3*self.last_PM10)
                                self.last_PM2_5 = pm2_5
                                self.last_PM10 = pm10      
                                self.gotRightData()

                                if can_send:
                                    return [{
                                        "name": "PM2.5",
                                        "symbol": "ug/m^3",
                                        "device": DeviceID,
                                        "sensor": PM2_5_SenorID,
                                        "data": pm2_5
                                    },
                                    {
                                        "name": "PM2.5_AQI",
                                        "symbol": "",
                                        "device": DeviceID,
                                        "sensor": PM2_5_AQI_SenorID,
                                        "data": int(aqi.to_iaqi(aqi.POLLUTANT_PM25, pm2_5, algo=aqi.ALGO_MEP))
                                    },
                                    {
                                        "name": "PM10",
                                        "symbol": "ug/m^3",
                                        "device": DeviceID,
                                        "sensor": PM10_SenorID,
                                        "data": pm10
                                    },
                                    {
                                        "name": "PM10_AQI",
                                        "symbol": "",
                                        "device": DeviceID,
                                        "sensor": PM10_AQI_SenorID,
                                        "data": int(aqi.to_iaqi(aqi.POLLUTANT_PM10, pm10, algo=aqi.ALGO_MEP))
                                    }]
                                else:
                                    print "异常: lastpm2.5="+str(last_PM2_5)+" pm2.5="+str(pm2_5) + "lastpm10="+str(last_PM10)+" pm10="+str(pm10)
                        
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
if __name__ == '__main__':
    sensor = PMS5003()
    #print sensor.GetData()
