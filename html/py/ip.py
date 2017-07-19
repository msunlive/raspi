# -*- coding: utf-8 -*-

import socket
import fcntl
import os
import struct
import time
import urllib
import urllib2

last_ip = ""

def get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', ifname[:15])
    )[20:24])

def uploadIP(ip):
    global last_ip
    
    if last_ip == "":
        pass
    elif ip == "":
        pass
    elif last_ip == ip:
        #ip 相同就不上报了
        print "ip 相同就不上报了 " + ip
        return
    
    url = "http://msun.gotoip1.com/php/respi.php?type=write_ip&name=respi&ip=" + ip
    req = urllib2.Request(url)
    print url
    res_data = urllib2.urlopen(req)
    res = res_data.read()
    #print res
    #print res.find("respi="+ip)
    if res.find("respi="+ip) == 0:
        #写入成功
        print "ip 上报成功 " + ip
        last_ip = ip        

def checkAndUpload():
    try:
        ip = get_ip_address("wlan0")
        uploadIP(ip)
    except IOError, e:
        print "没有连上wifi, 即将重启: " + str(e.args)
        os.system("sudo ifdown wlan0")
        time.sleep(1)
        os.system("sudo ifup wlan0")
        time.sleep(10)
        checkAndUpload()

print "start ip.py"
while 1:
    checkAndUpload()
    time.sleep(20)

    
