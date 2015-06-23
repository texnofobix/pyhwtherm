import pyhwtherm

mytest = pyhwtherm.PyHWTherm(
        username="someuser@example.com",
        password="mysecretpassword",
        deviceid=123456
        )

print "login successful: ",mytest.login()
print "Get thermostat data:", mytest.updateStatus()
beforeChange = mytest.status
print "Status: ", beforeChange
mytest.tempHold("11:00",cool=78,heat=68)

mytest.submit()

print "Get thermostat data:", mytest.updateStatus()
afterChange = mytest.status
print "heat >>",beforeChange['latestData']['uiData']['HeatSetpoint'],"->",afterChange['latestData']['uiData']['HeatSetpoint']
print "cool >>",beforeChange['latestData']['uiData']['CoolSetpoint'],"->",afterChange['latestData']['uiData']['CoolSetpoint']

print "Logout", mytest.logout()
