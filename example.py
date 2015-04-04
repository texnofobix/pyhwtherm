import pyhwtherm

mytest = pyhwtherm.PyHWTherm(
        username="someuser@example.com",
        password="mysecretpassword",
        deviceid=123456
        )

print mytest.login()
print mytest.query()

mytest.tempHold("09:00",cool=80,heat=72)

mytest.submit()

after = mytest.query()
print "heat >>",before['latestData']['uiData']['HeatSetpoint'],"->",after['latestData']['uiData']['HeatSetpoint']
print "cool >>",before['latestData']['uiData']['CoolSetpoint'],"->",after['latestData']['uiData']['CoolSetpoint']

mytest.logout()
