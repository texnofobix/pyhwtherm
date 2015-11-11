import unittest

from pyhwtherm import *

class TestPyHWTherm(unittest.TestCase):
    
    def setUp(self):
        self.username = 'user'
        self.password = 'pw'
        self.deviceid = 12345
        self.testtherm = PyHWTherm(self.username,self.password,self.deviceid)

    def testCreateObject(self):
        self.testtherm = PyHWTherm(
                self.username,
                self.password,
                self.deviceid
                )
        self.assertIsInstance(self.testtherm,PyHWTherm)

    def testGetUTC(self):
        self.assertIsInstance(self.testtherm.getutv(),str)
        
    def testPermBlank(self):
        prep = {
                "SystemSwitch": None,
                "HeatSetpoint": None,
                "CoolSetpoint": None,
                "HeatNextPeriod": None,
                "CoolNextPeriod": None,
                "StatusHeat": None,
                "StatusCool": None,
                "FanMode": None,
                "DeviceID": self.deviceid
                }

        prep["SystemSwitch"],None
        prep["HeatSetpoint"],None
        prep["CoolSetpoint"],None
        prep["HeatNextPeriod"],None
        prep["CoolNextPeriod"],None
        prep["StatusHeat"],None
        prep["StatusCool"],None
        prep["FanMode"],None

        self.testtherm.change_request.update(prep)

        self.assertEqual(self.testtherm.change_request,prep)
        #self.assertEqual(self.testtherm['DeviceID'],self.deviceid)
 
    
    def testHoldPerm(self):
        self.testtherm.temp(holdmode=Hold.PERMANENT)
        self.assertEqual(self.testtherm.change_request["StatusHeat"],Hold.PERMANENT)
        self.assertEqual(self.testtherm.change_request["StatusCool"],Hold.PERMANENT)

    def testHoldTemp(self):
        self.testtherm.temp(holdmode=Hold.TEMPORARY)
        self.assertEqual(self.testtherm.change_request["StatusHeat"],Hold.TEMPORARY)
        self.assertEqual(self.testtherm.change_request["StatusCool"],Hold.TEMPORARY)

    def testHoldPermHeat68Cool72(self):
        self.testtherm.temp(Hold.PERMANENT, cool=72, heat=68)
        self.assertEqual(self.testtherm.change_request["StatusHeat"],Hold.PERMANENT)
        self.assertEqual(self.testtherm.change_request["StatusCool"],Hold.PERMANENT)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],68)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],72)

    def testTempPermHeat68Cool72(self):
        self.testtherm.temp(holdmode=Hold.PERMANENT, cool=72, heat=68, holdtime="1:30")
        self.assertEqual(self.testtherm.change_request["StatusHeat"],Hold.PERMANENT)
        self.assertEqual(self.testtherm.change_request["StatusCool"],Hold.PERMANENT)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],68)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],72)
        self.assertEqual(self.testtherm.change_request["CoolNextPeriod"],6)
        self.assertEqual(self.testtherm.change_request["HeatNextPeriod"],6)

    def testHoldPerm(self):
        self.testtherm.temp(holdmode=Hold.PERMANENT)
        self.assertEqual(self.testtherm.change_request["StatusHeat"],Hold.PERMANENT)
        self.assertEqual(self.testtherm.change_request["StatusCool"],Hold.PERMANENT)

    def testTempHeat10Cool50(self):
        self.testtherm.temp(cool=50, heat=10)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],10)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],50)

    def testTempHeat68(self):
        self.testtherm.temp(heat=68)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],68)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],None)

    def testTempCool90(self):
        self.testtherm.temp(cool=90)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],None)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],90)

    def testTempTime(self):
        self.testtherm.temp(holdtime="01:30")
        self.assertEqual(self.testtherm.change_request["CoolNextPeriod"],6)
        self.assertEqual(self.testtherm.change_request["HeatNextPeriod"],6)

    def testFanOn(self):
        self.testtherm.fan(Fan.ON)
        self.assertEqual(self.testtherm.change_request["FanMode"],Fan.ON)

    def testFanAuto(self):
        self.testtherm.fan(Fan.AUTO)
        self.assertEqual(self.testtherm.change_request["FanMode"],Fan.AUTO)

    def testFanBad(self):
        self.assertEqual(self.testtherm.fan('bad'),False)
        
    def testSystemAuto(self):
        self.testtherm.system(System.AUTO)
        self.assertEqual(self.testtherm.change_request["SystemSwitch"],System.AUTO)
    
    def testSystemCool(self):
        self.testtherm.system(System.COOL)
        self.assertEqual(self.testtherm.change_request["SystemSwitch"],System.COOL)
        
    def testSystemHeat(self):
        self.testtherm.system(System.HEAT)
        self.assertEqual(self.testtherm.change_request["SystemSwitch"],System.HEAT)
        
    def testSystemOff(self):
        self.testtherm.system(System.OFF)
        self.assertEqual(self.testtherm.change_request["SystemSwitch"],System.OFF)
        
    def testSystemBad(self):
        self.assertEqual(self.testtherm.system('bad'),False)



if __name__ == '__main__':
    unittest.main()
