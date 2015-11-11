from pyhwtherm import *
from config import Thermostat


def test():
    thermostat = pyhwtherm.PyHWTherm(
        username=Thermostat["User"],
        password=Thermostat["Password"],
        deviceid=Thermostat["Deviceid"]
    )

    thermostat.DEBUG = 1

    # Login
    thermostat.login()

    # Test System
    # thermostat.system (System.OFF)
    # thermostat.system(System.HEAT)
    # thermostat.system (System.COOL)
    # thermostat.system (System.AUTO)

    # Test fan
    # thermostat.fan(Fan.ON)
    # thermostat.fan(Fan.AUTO)
    # thermostat.fan(Fan.CIRCULATE)
    # thermostat.fan(Fan.SCHEDULE)

    # Test temp
    # thermostat.temp(holdmode=Hold.PERMANENT, cool=72, heat=68)
    # thermostat.temp(holdmode=Hold.TEMPORARY, holdtime="8:00", cool=72, heat=68)
    # thermostat.temp(holdmode=Hold.TEMPORARY, holdtime=2, cool=72, heat=68)
    # thermostat.temp(holdmode=Hold.FOLLOWSCHEDULE)

    # Submit request
    # thermostat.submit()

    print ("*******************************************")
    print ("Thermostat data:", thermostat.updatestatus()), thermostat.VERSION
    print ("*******************************************")

    status = thermostat.status
    latestdata = status["latestData"]
    uidata = latestdata["uiData"]
    fandata = latestdata["fanData"]

    # Print Status
    print ("   ?SystemSwitchPosition: ", uidata["SystemSwitchPosition"], System.mode[uidata["SystemSwitchPosition"]])
    print ("   ?CoolSetpoint: ", uidata["CoolSetpoint"])
    print ("   ?CoolNextPeriod: ", thermostat.period2time(uidata["CoolNextPeriod"]), uidata["CoolNextPeriod"])
    print ("   ?StatusCool: ", uidata["StatusCool"])
    print ("   ?HeatSetpoint: ", uidata["HeatSetpoint"])
    print ("   ?HeatNextPeriod: ", thermostat.period2time(uidata["HeatNextPeriod"]), uidata["HeatNextPeriod"])
    print ("   ?StatusHeat:", uidata["StatusHeat"])
    print ("   ?TemporaryHoldUntilTime: ", thermostat.period2time(uidata["TemporaryHoldUntilTime"] / 15),
           uidata["TemporaryHoldUntilTime"])
    print ("   ?DispTemperature: ", uidata["DispTemperature"])
    print ("   ?IndoorHumidity: ", uidata["IndoorHumidity"])
    print ("   ?OutdoorTemperature: ", uidata["OutdoorTemperature"])
    print ("   ?OutdoorHumidity: ", uidata["OutdoorHumidity"])
    print ("   ?fanMode: ", fandata["fanMode"], Fan.mode[fandata["fanMode"]])

    # Log out
    thermostat.logout()


if __name__ == '__main__':
    test()
