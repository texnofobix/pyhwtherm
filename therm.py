#!/usr/bin/python


# Originally by Brad Goodman
# http://www.bradgoodman.com/
# brad@bradgoodman.com

# Thermostat controller


import urllib2
import urllib
import json
import datetime
import re
import time
import math
import base64
import time
import httplib
import sys
import tty,termios
import getopt
import os
import stat

# Optional - Specify credentials here so you don't need them on command line
#USERNAME="myusername"
#PASSWORD="mypassword"
#DEVICE_ID=00000

AUTH="https://rs.alarmnet.com/TotalConnectComfort/"

def get_login():
    
    print 
    print
    print "Run at ",datetime.datetime.now()
    retries=5
    params=urllib.urlencode({"timeOffset":"240",
        "UserName":USERNAME,
        "Password":PASSWORD,
        "RememberMe":"false"})
    #print params
    headers={"Content-Type":"application/x-www-form-urlencoded",
            "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding":"sdch",
            "Host":"rs.alarmnet.com",
            "DNT":"1",
            "Origin":"https://rs.alarmnet.com/TotalComfort/",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36"
        }
    conn = httplib.HTTPSConnection("rs.alarmnet.com")
    conn.request("POST", "/TotalConnectComfort/",params,headers)
    r1 = conn.getresponse()
    #print r1.status, r1.reason
    cookie = r1.getheader("Set-Cookie")
    location = r1.getheader("Location")
    #print "Cookie",cookie
    #print
    # Strip "expires" "httponly" and "path" from cookie
    newcookie=cookie
    newcookie=re.sub(";\s*expires=[^;]+","",newcookie)
    newcookie=re.sub(";\s*path=[^,]+,",";",newcookie)
    newcookie=re.sub("HttpOnly\s*[^;],","X;",newcookie)
    newcookie=re.sub(";\s*HttpOnly\s*,",";",newcookie)
    cookie=newcookie
    #print "Cookie",cookie


    if ((location == None) or (r1.status != 302)):
        raise BaseException("Login fail" )

def query():
    # Skip second query - just go directly to our device_id, rather than letting it
    # redirect us to it. 

    code=str(DEVICE_ID)

    t = datetime.datetime.now()
    utc_seconds = (time.mktime(t.timetuple()))
    utc_seconds = int(utc_seconds*1000)
    print "Code ",code

    location="/TotalConnectComfort/Device/CheckDataSession/"+code+"?_="+str(utc_seconds)
    #print "THIRD"
    headers={
            "Accept":"*/*",
            "DNT":"1",
            "Accept-Encoding":"plain",
            "Cache-Control":"max-age=0",
            "Accept-Language":"en-US,en,q=0.8",
            "Connection":"keep-alive",
            "Host":"rs.alarmnet.com",
            "Referer":"https://rs.alarmnet.com/TotalConnectComfort/",
            "X-Requested-With":"XMLHttpRequest",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            "Cookie":cookie
        }
    conn = httplib.HTTPSConnection("rs.alarmnet.com")
    conn.request("GET", location,None,headers)
    r3 = conn.getresponse()
    if (r3.status != 200):
			print "Bad R3 status ",r3.status, r3.reason
    #print r3.status, r3.reason
    rawdata=r3.read()
    j = json.loads(rawdata)
    #print json.dumps(j,sort_keys=True,indent=4, separators=(',', ': '))
    print "Success",j['success']
    print "Live",j['deviceLive']
    print "CurrentTemp",j['latestData']['uiData']["DispTemperature"]
    print "CoolSetponit",j['latestData']['uiData']["CoolSetpoint"]
    print "HoldUntil",j['latestData']['uiData']["TemporaryHoldUntilTime"]
    print "StatusCool",j['latestData']['uiData']["StatusCool"]
    print "StatusHeat",j['latestData']['uiData']["StatusHeat"]

def update():    
    if (queryOnly != None):
      return

    headers={
            "Accept":'application/json; q=0.01',
            "DNT":"1",
            "Accept-Encoding":"gzip,deflate,sdch",
            'Content-Type':'application/json; charset=UTF-8',
            "Cache-Control":"max-age=0",
            "Accept-Language":"en-US,en,q=0.8",
            "Connection":"keep-alive",
            "Host":"rs.alarmnet.com",
            "Referer":"https://rs.alarmnet.com/TotalConnectComfort/",
            "X-Requested-With":"XMLHttpRequest",
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36",
            'Referer':"/TotalConnectComfort/Device/CheckDataSession/"+code,
            "Cookie":cookie
        }

    t = datetime.datetime.now();
    tcode = t.hour * 60 + t.minute;
    holdtime=2
    if (raiseHold): holdtime=6
    t2code = ((t.hour+holdtime)%24) * 60 + t.minute
    t2code = t2code/15
    print "Current time code",tcode,"2-hours",t2code
    cancelHold= {
        "CoolNextPeriod": None,
        "CoolSetpoint": 75,
        "DeviceID": DEVICE_ID,
        "FanMode": None,
        "HeatNextPeriod": None,
        "HeatSetpoint": None,
        "StatusCool": 0,
        "StatusHeat": 0,
        "SystemSwitch": None
        }
    cool2Hold= {
        "CoolNextPeriod": t2code,
        "CoolSetpoint": 74,
        "DeviceID": DEVICE_ID,
        "FanMode": None,
        "HeatNextPeriod": t2code,
        "HeatSetpoint": None,
        "StatusCool": 1,
        "StatusHeat": 1,
        "SystemSwitch": None
        }

    setcool = None
    currentTemp =  j['latestData']['uiData']["DispTemperature"]
    coolSetPoint = j['latestData']['uiData']["CoolSetpoint"] 


    if (runProgram):
        print "Resume normal program"
    elif (raiseHold):
        print "Holding at 80 for 6 hours"
        setcool=80
    elif (coolSetPoint < currentTemp):
        print "Don't do anything - becasue we should already be cooling"
    elif ((currentTemp > 72) and (coolSetPoint > 72)):
        print "Let's try to get setpoint down to at least 72"
        setcool = 72
    else:
        setcool = int(currentTemp - 2)
        print "Drop setpoint to %s - becasue we're higher than that" % setcool
        
    if ((setcool==None) and (not runProgram)):
        return

    if (dontChange):
        print "Not Changing",dontChange
        return
    """
    print 
    print 
    print rawj
"""

    if (raiseHold):
        setcool=80

    location="/TotalConnectComfort/Device/SubmitControlScreenChanges"
    cool2Hold["CoolSetpoint"] = setcool
    rawj=""
    if (runProgram):
        rawj=json.dumps(cancelHold)
    else:
        rawj=json.dumps(cool2Hold)
    conn = httplib.HTTPSConnection("rs.alarmnet.com")
    #conn.set_debuglevel(999);
    conn.request("POST", location,rawj,headers)
    r4 = conn.getresponse()
    if (r4.status != 200): 
			print "Bad R4 status ",r4.status, r4.reason
    #print r4.read()

