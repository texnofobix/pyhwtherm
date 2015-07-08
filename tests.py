import unittest
from mock import Mock
from pyhwtherm import PyHWTherm

class TestPyHWTherm(unittest.TestCase):
    
    def setUp(self):
        self.username = 'user'
        self.password = 'pass'
        self.deviceid = 123456
        self.testtherm = PyHWTherm(self.username,self.password,self.deviceid)
        

    def testCreateObject(self):
        self.testtherm = PyHWTherm(
                self.username,
                self.password,
                self.deviceid
                )
        self.assertIsInstance(self.testtherm,PyHWTherm)


    def testGetUTC(self):
        self.assertIsInstance(self.testtherm.getUTC(),str)
        
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

        self.testtherm.permHold()
        self.assertEqual(self.testtherm.change_request,prep)
        #self.assertEqual(self.testtherm['DeviceID'],self.deviceid)

    def testPermHeat71(self):
        self.testtherm.permHold(heat=71)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],71)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],None)

    def testPermHeat10Cool50(self):
        self.testtherm.permHold(heat=10,cool=50)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],10)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],50)

    def testPermCool90(self):
        self.testtherm.permHold(cool=90)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],None)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],90)

    def testTempTime(self):
        self.testtherm.tempHold("01:30")
        self.assertEqual(self.testtherm.change_request["CoolNextPeriod"],6)
        self.assertEqual(self.testtherm.change_request["HeatNextPeriod"],6)

    def testFanOn(self):
        self.testtherm.fan("on")
        self.assertEqual(self.testtherm.change_request["FanMode"],PyHWTherm.FANON)

    def testFanAuto(self):
        self.testtherm.fan("auto")
        self.assertEqual(self.testtherm.change_request["FanMode"],PyHWTherm.FANAUTO)

    def testFanBad(self):
        self.assertEqual(self.testtherm.fan('durr'),False)
        
    def testSystemAuto(self):
        self.testtherm.systemState("auto")
        self.assertEqual(self.testtherm.change_request["SystemSwitch"],PyHWTherm.SYSTEMAUTO)
    
    def testSystemCool(self):
        self.testtherm.systemState("cool")
        self.assertEqual(self.testtherm.change_request["SystemSwitch"],PyHWTherm.SYSTEMCOOL)
        
    def testSystemHeat(self):
        self.testtherm.systemState("heat")
        self.assertEqual(self.testtherm.change_request["SystemSwitch"],PyHWTherm.SYSTEMHEAT)
        
    def testSystemOff(self):
        self.testtherm.systemState("off")
        self.assertEqual(self.testtherm.change_request["SystemSwitch"],PyHWTherm.SYSTEMOFF)
        
    def testSystemBad(self):
        self.assertEqual(self.testtherm.systemState('durr'),False)



if __name__ == '__main__':
    unittest.main()
