import requests
import datetime
import time
import json

#currently queries only

class hwtherm2(object):
    """
    PyHWTherm is Python code to connect to the Honeywell Thermostat (currently
    at https://rs.alarmnet.com/TotalConnectComfort) website to query and change
    settings.
    """
    HOST = 'rs.alarmnet.com'
    BASEURL = "https://" + HOST + "/TotalConnectComfort"
    FANAUTO = 0
    FANON = 1
    SYSTEMOFF = 2
    SYSTEMHEAT = 1
    SYSTEMCOOL = 3
    SYSTEMAUTO = 4

    deviceid = 0
    valid_login = False

    common_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0',
        'Host': HOST,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': BASEURL
        }

    query_headers = {
        "X-Requested-With": "XMLHttpRequest",
        'Accept': '*/*',
        }

    change_request = {
        "DeviceID": deviceid,
        "SystemSwitch": None,
        "HeatSetpoint": None,
        "CoolSetpoint": None,
        "HeatNextPeriod": None,
        "CoolNextPeriod": None,
        "StatusHeat": None,
        "StatusCool": None,
        "FanMode": None
        }


    def __init__(self, username, password, deviceid):
        """
        Create new object. Requires a valid Honeywell username (usually an
        email address), password, and deviceid number. The deviceid can be found
        after logging into the site for the respective device.
        """
        self.deviceid = int(deviceid)
        self.session = requests.Session()

        self._auth_requestparm = {
                'timeOffset': 240, 
                'RememberMe': 'false',
                'UserName': username,
                'Password': password,
            }

        self.query_headers["Referer"] = self.BASEURL + "/Device/Control/" + str(deviceid)
        self.change_request["DeviceID"] = int(deviceid)

    def login(self):
        """
        Logins to site and establishes a valid session using the stored
        credentials.
        """

        r_login = self.session.post(
                self.BASEURL,
                params = self._auth_requestparm,
                headers = self.common_headers
                )
        #print r_login.status_code,r_login.reason,r_login.text

        if r_login.text.find("Login was unsuccessful.") > 0:
            print "Login was unsuccessful."
            raise
            return False

        r_login.raise_for_status()

        self.valid_login = True

        return True

    def query(self):
        """
        Queries the site and returns thermostat data in dict
        """
        if not self.valid_login:
            print "Not logged in!"
            return False

        query_headers = dict(self.common_headers, **self.query_headers)

        r_query = self.session.get(
                self.BASEURL + 
                '/Device/CheckDataSession/' + 
                str(self.deviceid) + 
                '?_=' + 
                self.getUTC(),
                headers = query_headers)
        r_query.raise_for_status()
        return r_query.json()

    def getUTC(self):
        t = datetime.datetime.now()
        utc_seconds = (time.mktime(t.timetuple()))
        utc_seconds = int(utc_seconds*1000)
        return str(utc_seconds)


    def submit(self, send=True):
        set_headers = dict(self.common_headers, **self.query_headers)
        set_headers['Content-type'] = "application/json; charset=utf-8"
        #print set_headers

        #print "json"
        #print self.change_request
        #print json.dumps(self.change_request)

        if send:
            r=self.session.post(
                    self.BASEURL + '/Device/SubmitControlScreenChanges',
                    data=json.dumps(self.change_request),
                    headers=set_headers)
            r.raise_for_status()

            #Verify success
            if json.loads(r.text)["success"] != 1:
                raise "submit error"


    def permHold(self, heat=None, cool=None):
        prep = {
                "SystemSwitch": None,
                "HeatSetpoint": None,
                "CoolSetpoint": None,
                "HeatNextPeriod": None,
                "CoolNextPeriod": None,
                "StatusHeat": None,
                "StatusCool": None,
                "FanMode": None
                }

        if heat is not None:
            prep["HeatSetpoint"] = int(heat)

        if cool is not None:
            prep["CoolSetpoint"] = int(cool)

        self.change_request.update(prep)
        #print "Value : %s" %  self.change_request
    
    def tempHold(self,intime, cool=None, heat=None):
        """
        Not finished
        """
        inputTime = time.strptime(intime, "%H:%M")
        intime = (inputTime.tm_hour * 60 + inputTime.tm_min) / 15
        
        preptemp = { "StatusHeat":1, "StatusCool":1 }
        
        if heat is not None:
            preptemp["HeatSetpoint"] = int(heat)

        if cool is not None:
            preptemp["CoolSetpoint"] = int(cool)

        preptemp["CoolNextPeriod"] = int(intime)
        preptemp["HeatNextPeriod"] = int(intime)

        self.change_request.update(preptemp)
        #print "Value : %s" %  self.change_request

    def cancelHold(self):
        """
        set to ScheduleHeat/CoolSp in r_query.json()
        {"DeviceID":0,"SystemSwitch":null,"HeatSetpoint":70,"CoolSetpoint":78,"HeatNextPeriod":null,"CoolNextPeriod":null,"StatusHeat":0,"StatusCool":0,"FanMode":null}
        """
        prepcancel = { "StatusHeat":0, "StatusCool":0,
                "HeatNextPeriod":None,"CoolNextPeriod":None
                }
        self.change_request.update(prepcancel)

    def fan(self,mode):
        if mode.upper() == 'ON':
            self.change_request["FanMode"]=self.FANON
        elif mode.upper() == 'AUTO': 
            self.change_request["FanMode"]=self.FANAUTO
        else:
            return False
        return self.change_request["FanMode"]
