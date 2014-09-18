from hwtherm2 import hwtherm2

mytest = hwtherm2(
        username="someuser@example.com",
        password="mysecretpassword",
        deviceid=123456
        )

print mytest.login()
print mytest.query()
