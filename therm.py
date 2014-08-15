#!/usr/bin/python


# Originally by Brad Goodman
# http://www.bradgoodman.com/
# brad@bradgoodman.com

#Functionalized by texnofobix

# Thermostat controller

import urllib
import json
import datetime
import re
import time
import math
import time
import httplib

# Optional - Specify credentials here so you don't need them on command line
#USERNAME="myusername"
#PASSWORD="mypassword"
#DEVICE_ID=00000

AUTH="https://rs.alarmnet.com/TotalConnectComfort/"

thermo_request = {
        "DeviceID": DEVICE_ID,
        "SystemSwitch": None,
        "HeatSetpoint": None,
        "CoolSetpoint": None,
        "HeatNextPeriod": None,
        "CoolNextPeriod": None,
        "StatusHeat": None,
        "StatusCool": None,
        "FanMode": None

    }

def get_login():
    global cookie #cookie is requried between query and update
    
    print 
    print
    print "Run at ",datetime.datetime.now()
    retries=5
    params=urllib.urlencode({"timeOffset":"240",
        "UserName":USERNAME,
        "Password":PASSWORD,
        "RememberMe":"false"})

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
    cookie = r1.getheader("Set-Cookie")
    location = r1.getheader("Location")
    # Strip "expires" "httponly" and "path" from cookie
    newcookie=cookie
    newcookie=re.sub(";\s*expires=[^;]+","",newcookie)
    newcookie=re.sub(";\s*path=[^,]+,",";",newcookie)
    newcookie=re.sub("HttpOnly\s*[^;],","X;",newcookie)
    newcookie=re.sub(";\s*HttpOnly\s*,",";",newcookie)
    cookie = newcookie

    if ((location == None) or (r1.status != 302)):
        raise BaseException("Login fail" )
    
    return cookie

def query():
    # Skip second query - just go directly to our device_id, rather than letting it
    # redirect us to it. 

    t = datetime.datetime.now()
    utc_seconds = (time.mktime(t.timetuple()))
    utc_seconds = int(utc_seconds*1000)
    
    location="/TotalConnectComfort/Device/CheckDataSession/"+str(DEVICE_ID)+"?_="+str(utc_seconds)
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
    current_therm = json.loads(rawdata)
    
    print "Success",current_therm['success']
    print "Live",current_therm['deviceLive']
    print "CurrentTemp",current_therm['latestData']['uiData']["DispTemperature"]
    print "CoolSetpoint",current_therm['latestData']['uiData']["CoolSetpoint"]
    print "HoldUntil",current_therm['latestData']['uiData']["TemporaryHoldUntilTime"]
    print "StatusCool",current_therm['latestData']['uiData']["StatusCool"]
    print "StatusHeat",current_therm['latestData']['uiData']["StatusHeat"]

def update():    
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
            'Referer':"/TotalConnectComfort/Device/CheckDataSession/"+str(DEVICE_ID),
            "Cookie":cookie
        }

    #update the thermo_request block like below.
    thermo_request["CoolSetpoint"] = 80
    
    location="/TotalConnectComfort/Device/SubmitControlScreenChanges"
    rawj="" #clearing previous if existing
    rawj=json.dumps(thermo_request)
    conn = httplib.HTTPSConnection("rs.alarmnet.com")
    conn.request("POST", location,rawj,headers)
    r4 = conn.getresponse()
    if (r4.status != 200): 
			print "Bad R4 status ",r4.status, r4.reason

get_login()
query()
update()
query()