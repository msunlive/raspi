# -*- coding: utf-8 -*- 
import os
import sys
import imp
import thread
import threading
import time
import datetime
import requests
import json
import wiringpi

DVK512 = True

api_url='http://api.yeelink.net/v1.0'
api_key='12ecc2de29795681493cf4b4f28fe4a2'
api_headers={'U-ApiKey':api_key,'content-type': 'application/json'}

sensors = []
datas = []
lcdFD = None
threadLock = threading.Lock()

def logout(str):
    print "%s %s"%(datetime.datetime.now().strftime("%m-%d %H:%M:%S.%f")[:-3], str)
    sys.stdout.flush()

def upload_data_to_yeelink(device, sensor, data):
    url=r'%s/device/%s/sensor/%s/datapoints' % (api_url,device,sensor)
    strftime=time.strftime("%Y-%m-%dT%H:%M:%S")
    data={"timestamp":strftime , "value": data}
    res=requests.post(url,headers=api_headers,data=json.dumps(data),timeout=30)
    if res.status_code != 200:
        return (False, res.status_code)
    else:
        return (True, None)

def load_sensors():
    sensor_path = os.path.abspath("Sensor") + "/"
    sensor_files = os.listdir(sensor_path)

    for filename in sensor_files:
        if filename[-3:] != ".py":
            continue
        try:
            sensor_name = filename[:-3]
            #print sensor_name
            module = imp.load_source(sensor_name, sensor_path + filename)
            class_obj = getattr(module, sensor_name)
            instance = class_obj()
            sensors.append(instance)
        except Exception, e:
            logout("Sensor %s load error:%s"%(filename, e)) 

def run():
    while True:
        global datas
        lst = []
        all_ready = True
        for sensor in sensors:
            try:                
                #logout("Sensor %s fetching data..."%sensor.__class__.__name__) 
                result = sensor.GetData()
                all_ready &= sensor.isReady()
                #logout("Fetched:%s"%str(result))
                
                #如果result为空，表明超时
                if len(result) == 0:
                    sensor.waitDataTimeout()
                else:               
                    for data in result:
                        lst.append(data)
                        res, err = upload_data_to_yeelink(data["device"], data["sensor"], data["data"])
                        #logout("SensorID: %s Uploaed: %s"%(str(data["sensor"]), "Success" if res else "Failed: %s"%err)) 
            except Exception, e:
                logout(sensor.__class__.__name__+" : "+str(e))
                sensor.gotRightData(False)
        threadLock.acquire()
        datas = lst
        threadLock.release()
        #logout( "Sleep")
        #全部仪器ok后再恢复成2秒一次
        time.sleep(2 if all_ready else 0.2)

def showSensors():
    global lcdFD
    global datas

    while True:
        threadLock.acquire()
        lst = datas
        threadLock.release()
        for x in xrange(0, len(lst)):
            wiringpi.lcdClear(lcdFD)
            data1 = lst[x]
            wiringpi.lcdPosition(lcdFD, 0,0)
            wiringpi.lcdPrintf(lcdFD,"%s:"%(data1["name"]))
            wiringpi.lcdPosition(lcdFD, 0,1)
            wiringpi.lcdPrintf(lcdFD,"%s%s"%(data1["data"],data1["symbol"]))
            time.sleep(5)
            

def initLCD_DVK512():
    global lcdFD

    RS = 3
    EN = 14
    D0 = 4
    D1 = 12
    D2 = 13
    D3 = 6

    wiringpi.wiringPiSetup()
    lcdFD = wiringpi.lcdInit(2, 16, 4, RS, EN, D0, D1, D2, D3, 0, 0, 0, 0);

def initLCD_Custom():
    global lcdFD

    RS = 11
    EN = 10
    D0 = 0
    D1 = 1
    D2 = 2
    D3 = 3
    D4 = 4
    D5 = 5
    D6 = 6
    D7 = 7

    wiringpi.wiringPiSetup()
    lcdFD = wiringpi.lcdInit(2, 16, 8, RS, EN, D0, D1, D2, D3, D4, D5, D6, D7);


if __name__ == '__main__':
    print "start yeelink_uploader"
    load_sensors()
    if DVK512:
        initLCD_DVK512()
    else:    
        initLCD_Custom()

    thread.start_new_thread(run, ())
    showSensors()
