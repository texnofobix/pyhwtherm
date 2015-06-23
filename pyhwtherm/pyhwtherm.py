import requests
import datetime
import time
import json

class PyHWTherm(object):
    """
    PyHWTherm is Python code to connect to the Honeywell Thermostat (currently
    at https://mytotalconnectcomfort.com/portal/TotalConnectComfort) website to 
    query and change settings.
    """
    HOST = 'mytotalconnectcomfort.com'
    BASEURL = "https://" + HOST + "/portal"
    FANAUTO = 0
    FANON = 1
    SYSTEMOFF = 2
    SYSTEMHEAT = 1
    SYSTEMCOOL = 3
    SYSTEMAUTO = 4

    deviceid = 0
    valid_login = False

    common_headers = {
        'User-Agent': 'pyhwtherm/0.0.1',
        'Host': HOST,
        'Accept': 'application/json',
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

	body = self._auth_requestparm
	myheaders = self.common_headers

        self._r = self.session.post(
                self.BASEURL,
                data = self._auth_requestparm,
                headers = self.common_headers
                )

        if self._r.text.find("Login was unsuccessful.") > 0:
            print "Login was unsuccessful."
            raise
            return False

        self._r.raise_for_status()

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

        self._r = self.session.get(
                self.BASEURL + 
                '/Device/CheckDataSession/' + 
                str(self.deviceid) + 
                '?_=' + 
                self.getUTC(),
                headers = query_headers)
        self._r.raise_for_status()
       
        return self._r.json()

    def updateStatus(self):  
        """
        Query and set status.
        """    
        self.status = self.query()
        if self.status['success']:
            return True
        else:
            return False

    def getUTC(self):
        """ Creates UTC time string """
        t = datetime.datetime.now()
        utc_seconds = (time.mktime(t.timetuple()))
        utc_seconds = int(utc_seconds*1000)
        return str(utc_seconds)


    def submit(self, send=True):
        """ Submits change_request to site """
        set_headers = dict(self.common_headers, **self.query_headers)
        set_headers['Content-type'] = "application/json; charset=utf-8"

        if send:
            self._r=self.session.post(
                    self.BASEURL + '/Device/SubmitControlScreenChanges',
                    data=json.dumps(self.change_request),
                    headers=set_headers)
            self._r.raise_for_status()

            #Verify success
            if json.loads(self._r.text)["success"] != 1:
                raise "submit error"


    def permHold(self, heat=None, cool=None):
        """
        Sets the request to a permanent hold
        """

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
        Sets the change request to a temporary hold
        """
        inputTime = time.strptime(intime, "%H:%M")
        intime = (inputTime.tm_hour * 60 + inputTime.tm_min) / 15
        
        preptemp = { "StatusHeat": 1, "StatusCool": 1 }
        
        if heat is not None:
            preptemp["HeatSetpoint"] = int(heat)

        if cool is not None:
            preptemp["CoolSetpoint"] = int(cool)

        preptemp["CoolNextPeriod"] = int(intime)
        preptemp["HeatNextPeriod"] = int(intime)

        self.change_request.update(preptemp)

    def cancelHold(self):
        """
        Sets change_request to cancel the holds

        To Do: set to ScheduleHeat/CoolSp in r_query.json()
            {"DeviceID":0,"SystemSwitch":null,
            "HeatSetpoint":70,"CoolSetpoint":78,
            "HeatNextPeriod":null,"CoolNextPeriod":null,
            "StatusHeat":0,"StatusCool":0,"FanMode":null}
        """
        prepcancel = { "StatusHeat": 0, "StatusCool": 0,
                "HeatNextPeriod": None,"CoolNextPeriod": None
                }
        self.change_request.update(prepcancel)

    def fan(self,mode):
	"""
	Sets the request for fan as on or auto
	"""
        if mode.upper() == 'ON':
            self.change_request["FanMode"]=self.FANON
        elif mode.upper() == 'AUTO': 
            self.change_request["FanMode"]=self.FANAUTO
        else:
            return False
        return self.change_request["FanMode"]

    def logout(self):
    	"""
    	Logs out of the Honeywell site
    	"""
    	if (self.valid_login):
                self._r = requests.get("https://mytotalconnectcomfort.com/portal/Account/LogOff")
        self.valid_login = False
        return self._r.ok
    

