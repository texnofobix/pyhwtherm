#!/usr/bin/python


# By Brad Goodman
# http://www.bradgoodman.com/
# brad@bradgoodman.com

# Thermostat controller
# sudo nohup /usr/bin/python /home/bkg/therm.py /dev/input/ttyACM0 > /home/bkg/public_html/therm.out

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

# Returns character or None on error. Error should WAIT then retry
def getch(ttydev):
    fd=None
    old_settings=None
    ch=None
    try:
        fd = open(ttydev,"r")
        old_settings=termios.tcgetattr(fd)	
        tty.setraw(fd)
        ch = fd.read(1)
    finally:
         if (fd != None): 
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
         return ch


def get_login(queryOnly=None,raiseHold=None,dontChange=None,runProgram=None):
    
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
    #newcookie=re.sub("^expires=[^;]+;","",newcookie)
    #newcookie=re.sub("^expires=[^;]+$","",newcookie)
    newcookie=re.sub(";\s*expires=[^;]+","",newcookie)
    #newcookie=re.sub("^path=[^;]+;","",newcookie)
    #newcookie=re.sub(";\s*path=[^;]+;",";",newcookie)
    newcookie=re.sub(";\s*path=[^,]+,",";",newcookie)
    newcookie=re.sub("HttpOnly\s*[^;],","X;",newcookie)
    newcookie=re.sub(";\s*HttpOnly\s*,",";",newcookie)
    cookie=newcookie
    #print "Cookie",cookie


    if ((location == None) or (r1.status != 302)):
        raise BaseException("Login fail" )


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
            #"Accept-Encoding":"gzip,deflate,sdch",
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
    #conn.set_debuglevel(999);
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
    print 
    print 
    print "Location",location
    for (k,v) in headers.iteritems():
        print k,v
    print 
    print 
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

"""
CancelHold
CoolNextPeriod: null
CoolSetpoint: 75
DeviceID: {{DEVICE_ID}}
FanMode: null
HeatNextPeriod: null
HeatSetpoint: null
StatusCool: 0
StatusHeat: 0
SystemSwitch: null

Set explicit cool setpoint
CoolNextPeriod: null
CoolSetpoint: 74
DeviceID: {{DEVICE_ID}}
FanMode: null
HeatNextPeriod: null
HeatSetpoint: null
StatusCool: 1
StatusHeat: 1
SystemSwitch: null

POST
Content-Type:application/json; charset=UTF-8
https://rs.alarmnet.com/TotalConnectComfort/Device/SubmitControlScreenChanges

Accept:application/json, text/javascript, */*; q=0.01
Accept-Encoding:gzip,deflate,sdch
Accept-Language:en-US,en;q=0.8
Connection:keep-alive
Content-Length:166
Content-Type:application/json; charset=UTF-8
Cookie:ASP.NET_SessionId=kkotsl4wqcmxktadj0qqrlqv; RememberMe={{USERNAME}}; .ASPXAUTH_TH_A=4E96C23A36F9390F15F7E83E552AB8DB6B3DC00FE62D88D1F3BC7EE19101747AB1F6E22FCEF78A4EE0B785C8402A52AC985B2C5C43EC01D3B90EE22B3DE64DCF8A15D53DDD01795382F0ABFC09451FE6D70B6B1CB9FD8752C3BC3D1171FE8943D6E2C1E6464BD851D0E7136344AB0830B5B05893CD0935A882E648DA06207AC8D4B67E86A74BEA7736651C0F610AC90EB22F3A03D459CCCB7B552668EC346AF7; TrueHomeCheckCookie=; thlang=en-US; __utma=95700044.1206170533.1376491635.1376491635.1376508195.2; __utmb=95700044.6.10.1376508195; __utmc=95700044; __utmz=95700044.1376508195.2.2.utmcsr=wifithermostat.com|utmccn=(referral)|utmcmd=referral|utmcct=/GetConnected/
DNT:1
Host:rs.alarmnet.com
Origin:https://rs.alarmnet.com
Referer:https://rs.alarmnet.com/TotalConnectComfort/Device/Control/{{DEVICE_ID}}
User-Agent:Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.95 Safari/537.36
X-Requested-With:XMLHttpRequest
Request Payloadview source
{DeviceID:{{DEVICE_ID}}, SystemSwitch:null, HeatSetpoint:null, CoolSetpoint:74, HeatNextPeriod:null,...}
"""

def usage():
    print """
    therm [optons] [ttydev]
    Options:
        -d  Don really do anyththing
        -r  Raise and hold temperature
        -p  Run normal Program
        -q  Query Only
        -U username
        -P password
        -D device_id
    If no options are given, a ttydef must be specified for interactive
    mode. Interactive mode keys are:
    Q    quit
    q    query
    C    Change Coolpoint
    r    Raise and hold temperature
    p    Run normal program (cancel holds)
    """

dontChange=None
raiseHold=None
runProgram=None
queryOnly=None
args=[]
try:
    opts,args=getopt.getopt(sys.argv[1:],"drpqP:U:D:")
except getopt.GetoptError as err:
    print str(err)
    usage()
    sys.exit(2)

for o,a in opts:
    if o== '-d':
        dontChange=1
    if o== '-r':
        raiseHold=1
    if o== '-p':
        runProgram=1
    if o== '-q':
        queryOnly=1
    if o== '-P':
        PASSWORD=a
    if o== '-U':
        USERNAME=a
    if o== '-D':
        DEVICE_ID=int(a)

if ((USERNAME == None) or (USERNAME=="") or (PASSWORD == None) or (PASSWORD == "") or (DEVICE_ID ==0)):
  print "User credentials not specified"
  exit(1)


if (raiseHold):
    print "RaiseHold"
    get_login(raiseHold=raiseHold)
    exit(0)

if (queryOnly):
    print "queryOnly"
    get_login(queryOnly=1)
    exit(0)

if (runProgram):
    print "runProgram"
    get_login(runProgram=runProgram)
    exit(0)


# We need a tty 

if (args.__len__() == 0):
    usage()
    exit(2)

ttydev=args.pop()
mode  = os.stat(ttydev).st_mode
if (not stat.S_ISCHR(mode)):
    print ttydev,"is not a character device"
    exit(2)

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
print "Interactive mode started",datetime.datetime.now()
while(1):
    ch = getch(ttydev)
    print ch
    if (ch == None):
        time.sleep(60)
    elif (ch == chr(3)):
        exit(1)
    elif (ch == 'Q'):
        exit(1)
    elif (ch == 'q'):
        d=get_login(queryOnly=1)
    elif (ch == 'p'):
        d=get_login(runProgram=1)
    elif (ch == 'r'):
        d=get_login(raiseHold=1)
    elif (ch == 'C'):
        d=get_login(dontChange=dontChange)
