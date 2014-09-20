import unittest
import hwtherm2

class TestHWTherm2(unittest.TestCase):
    
    def setUp(self):
        self.username = 'user'
        self.password = 'pass'
        self.deviceid = 123456
        self.testtherm = hwtherm2.hwtherm2(self.username,self.password,self.deviceid)

    def testCreateObject(self):
        self.testtherm = hwtherm2.hwtherm2(
                self.username,
                self.password,
                self.deviceid
                )
        self.assertIsInstance(self.testtherm,hwtherm2.hwtherm2)


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

        self.testtherm.perm()
        self.assertEqual(self.testtherm.change_request,prep)
        #self.assertEqual(self.testtherm['DeviceID'],self.deviceid)

    def testPermHeat71(self):
        self.testtherm.perm(heat=71)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],71)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],None)

    def testPermHeat10Cool50(self):
        self.testtherm.perm(heat=10,cool=50)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],10)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],50)

    def testPermCool90(self):
        self.testtherm.perm(cool=90)
        self.assertEqual(self.testtherm.change_request["HeatSetpoint"],None)
        self.assertEqual(self.testtherm.change_request["CoolSetpoint"],90)

    def testTempTime(self):
        self.testtherm.temp("01:30")
        self.assertEqual(self.testtherm.change_request["CoolNextPeriod"],6)
        self.assertEqual(self.testtherm.change_request["HeatNextPeriod"],6)



if __name__ == '__main__':
    unittest.main()
