import sys
import sched
import time

import MySQLdb as mdb

import pyhwtherm
from config import Thermostat, Database

laststatus=0;

dburl = Database["URL"]
dbuser = Database["User"]
dbpw = Database["Password"]
db = Database["Database"]
dbtable = Database["Table"]
deviceid=0

def timer(sc):
    updatedb()
    sc.enter(5, 1, timer, (sc,))

def dbTimeStamp():
    a = time.strftime('%Y-%m-%d %H:%M:%S')
    return str (a)

def updatedb():

    global laststatus
    global dbuser
    global dbpw
    global db

    t = pyhwtherm.PyHWTherm(
		username=Thermostat["User"],
        password=Thermostat["Password"],
        deviceid=Thermostat["Deviceid"]
    )
	
    try:
        t.login()
    except:
        print dbTimeStamp(),": Login error...."

    try:
        t.updatestatus()
    except:
        print(dbTimeStamp(),":Update error....")
	
    status = t.status
    if (laststatus != t.status):
        print dbTimeStamp(), ": Status changed, updating DB!!!"
        laststatus = status
        print laststatus
        latestdata = status["latestData"]
        uidata = latestdata["uiData"]
        fandata = latestdata["fanData"]

        print "*******************************************"
        print dbTimeStamp(),": Thermostat data:"
        print "*******************************************"
        print "   ?TimeStamp",  dbTimeStamp()
        print "   ?DeviceID",  deviceid
        print "   ?SystemSwitchPosition: ",uidata["SystemSwitchPosition"]
        print "   ?CoolSetpoint: ",uidata["CoolSetpoint"]
        print "   ?CoolNextPeriod: ", uidata["CoolNextPeriod"]
        print "   ?StatusCool: ",uidata["StatusCool"]
        print "   ?HeatSetpoint: ",uidata["HeatSetpoint"]
        print "   ?HeatNextPeriod: ", uidata["HeatNextPeriod"]
        print "   ?StatusHeat:" , uidata["StatusHeat"]
        print "   ?TemporaryHoldUntilTime: ", uidata["TemporaryHoldUntilTime"]
        print "   ?DispTemperature: ",uidata["DispTemperature"]
        print "   ?IndoorHumidity: ",uidata["IndoorHumidity"]
        print "   ?OutdoorTemperature: ",uidata["OutdoorTemperature"]
        print "   ?OutdoorHumidity: ",uidata["OutdoorHumidity"]
        print "   ?fanMode: ",fandata["fanMode"]

        try:
            dbcon = mdb.connect(dburl, dbuser, dbpw, db)
            c = dbcon.cursor()
            c.execute("insert into  " + dbtable + " ("
                      "DateTime, "
                      "Device, "
                      "SystemSwitchPosition, "
                      "CoolSetpoint, "
                      "CoolNextPeriod, "
                      "StatusCool, "
                      "HeatSetpoint, "
                      "HeatNextPeriod, "
                      "StatusHeat, "
                      "TemporaryHoldUntilTime, "
                      "DispTemperature,"
                      "IndoorHumidity,"
                      "OutdoorTemperature,"
                      "OutdoorHumidity,"
                      "fanMode)"#
                "values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);",
                (
                 dbTimeStamp(),
                 deviceid,
                 uidata["SystemSwitchPosition"],
                 uidata["CoolSetpoint"],
                 uidata["CoolNextPeriod"],
                 uidata["StatusCool"],
                 uidata["HeatSetpoint"],
                 uidata["HeatNextPeriod"],
                 uidata["StatusHeat"],
                 uidata["TemporaryHoldUntilTime"],
                 uidata["DispTemperature"],
                 uidata["IndoorHumidity"],
                 uidata["OutdoorTemperature"],
                 uidata["OutdoorHumidity"],
                 fandata["fanMode"] ))
            dbcon.commit()
        except mdb.Error, e:
            print "Error %d: %s" % (e.args[0], e.args[1])
            sys.exit(1)
        finally:
            if dbcon:
                dbcon.close()
        t.logout()
    else:
        print dbTimeStamp(),": Status NOT changed!!!"

if __name__ == '__main__':
    s = sched.scheduler(time.time, time.sleep)
    s.enter(0, 1, timer, (s, ))
    s.run()
