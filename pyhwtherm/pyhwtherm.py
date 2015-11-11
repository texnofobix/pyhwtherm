"""
PyHWTherm is Python code module to connect to the Honeywell Thermostat (currently
at https://mytotalconnectcomfort.com/portal/TotalConnectComfort) website to 
query and change settings.
Based on:
Original concept from http://www.bradgoodman.com/thermostat/
"""

import datetime
import time
import json
import requests


class Fan:
    def __init__(self):
        pass

    mode = ['Auto', 'On', 'Circulate', 'Follow Schedule']
    AUTO = 0
    ON = 1
    CIRCULATE = 2
    FOLLOWSCHEDULE = 3


class Hold:
    def __init__(self):
        pass

    mode = ['Follow Schedule', 'Temporary Hold', 'Permanent Hold']
    FOLLOWSCHEDULE = 0
    TEMPORARY = 1
    PERMANENT = 2


class System:
    def __init__(self):
        pass

    mode = ['?', 'Heat', 'Off', 'Cool', 'Auto', '?']
    OFF = 2
    HEAT = 1
    COOL = 3
    AUTO = 4


class PyHWTherm(object):
    VERSION = 2.0

    # Set DEBUG to 1 to show debug output, > 1 to show verbose debug
    DEBUG = 0
    deviceid = 0
    valid_login = False

    HOST = 'mytotalconnectcomfort.com'
    BASEURL = "https://" + HOST + "/portal"

    common_headers = {
        'User-Agent': 'PyHWTherm/'+str(VERSION),
        'Host': HOST,
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': BASEURL
    }

    query_headers = {
        "X-Requested-With": "XMLHttpRequest",
        'Accept': '*/*',
        'Referer': BASEURL
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

        self.auth_requestparm = {
            'timeOffset': 240,
            'RememberMe': 'false',
            'UserName': username,
            'Password': password,
        }

        self.query_headers["Referer"] = self.BASEURL + "/Device/Control/" + str(deviceid)
        self.change_request["DeviceID"] = int(deviceid)
        self.status = ""

    def version(self):
        return self.VERSION

    def login(self):
        """
        Login to site and establishes a valid session using the stored
        credentials.
        """

        if self.DEBUG > 0:
            print (">login()")

        _auth = self.auth_requestparm
        _headers = self.common_headers

        if self.DEBUG > 0:
            print ("?self.BASEURL: ", self.BASEURL)
            print ("?_auth: ", _auth)
            print ("?_headers: ", _headers)

        response = self.session.post(
            self.BASEURL,
            data=_auth,
            headers=_headers
        )

        if self.DEBUG > 1:
            print (response.text)

        if response.text.find("Login was unsuccessful.") > 0:
            if self.DEBUG > 0:
                print ("<login() = False")
            return False

        response.raise_for_status()

        self.valid_login = True

        if self.DEBUG > 0:
            print ("<login() = True")

        return True

    def query(self):
        """
        Queries the site and returns thermostat data in dict
        """
        if self.DEBUG > 0:
            print (">query")

        if not self.valid_login:
            if self.DEBUG > 0:
                print (">query() = False")
            return False

        query_headers = dict(self.common_headers, **self.query_headers)
        baseurl = self.BASEURL + '/Device/CheckDataSession/' + str(self.deviceid) + '?_=' + self.getutv()

        if self.DEBUG > 0:
            print ("?baseurl: ", baseurl)
            print ("?query_headers: ", query_headers)

        query_req = self.session.get(
            baseurl,
            headers=query_headers)

        query_req.raise_for_status()

        if self.DEBUG > 0:
            print ("?resp: ", query_req.json())
            print ("<query()")

        return query_req.json()

    def updatestatus(self):
        """
        Query and set status.
        """
        self.status = self.query()
        if self.status['success']:
            return True
        else:
            return False

    # noinspection PyMethodMayBeStatic
    def getutv(self):
        """ Creates UTC time string """
        t = datetime.datetime.now()
        utc_seconds = (time.mktime(t.timetuple()))
        utc_seconds = int(utc_seconds * 1000)
        return str(utc_seconds)

    def submit(self, send=True):
        """ Submits change_request to site """
        if self.DEBUG > 0:
            print (">submit")

        set_headers = dict(self.common_headers, **self.query_headers)
        set_headers['Content-type'] = "application/json; charset=utf-8"

        if send:

            baseurl = self.BASEURL + '/Device/SubmitControlScreenChanges'
            reqdata = json.dumps(self.change_request)
            if self.DEBUG > 0:
                print ("?baseurl: ", baseurl)
                print ("?reqdata: ", reqdata)
                print ("?set_headers: ", set_headers)

            response = self.session.post(
                baseurl,
                data=reqdata,
                headers=set_headers)
            response.raise_for_status()

            # Verify success
            if json.loads(response.text)["success"] != 1:
                if self.DEBUG > 0:
                    print ("<submit() = False")
                raise Exception("submit error")
        if self.DEBUG > 0:
            print ("<submit() = true")

    # deprecated, use temp and hold
    # noinspection PyPep8Naming
    def permHold(self, heat=None, cool=None):
        self.temp(holdmode=Hold.PERMANENT, cool=cool, heat=heat)

    # deprecated, use temp and hold
    # noinspection PyPep8Naming
    def tempHold(self, intime, cool=None, heat=None):
        self.temp(holdmode=Hold.TEMPORARY, holdtime=intime, cool=cool, heat=heat)

    def hold(self, holdmode=None, holdtime=None):

        if holdmode is Hold.FOLLOWSCHEDULE:
            self.change_request["StatusHeat"] = int(Hold.FOLLOWSCHEDULE)
            self.change_request["StatusCool"] = int(Hold.FOLLOWSCHEDULE)
            return 0
        else:
            if holdmode is Hold.TEMPORARY:
                self.change_request["StatusHeat"] = int(Hold.TEMPORARY)
                self.change_request["StatusCool"] = int(Hold.TEMPORARY)
            else:
                if holdmode is Hold.PERMANENT:
                    self.change_request["StatusHeat"] = int(Hold.PERMANENT)
                    self.change_request["StatusCool"] = int(Hold.PERMANENT)
                else:
                    self.change_request["StatusHeat"] = None
                    self.change_request["StatusCool"] = None

        if holdtime is not None:
            if holdtime is 0:
                self.change_request["StatusHeat"] = int(Hold.PERMANENT)
                self.change_request["StatusCool"] = int(Hold.PERMANENT)
                self.change_request["HeatNextPeriod"] = 0
                self.change_request["CoolNextPeriod"] = 0
            else:
                if ":" in str(holdtime):
                    inputtime = time.strptime(holdtime, "%H:%M")
                    stop_time = (inputtime.tm_hour * 60 + inputtime.tm_min) / 15
                    self.change_request["CoolNextPeriod"] = stop_time
                    self.change_request["HeatNextPeriod"] = stop_time
                else:
                    t = datetime.datetime.now()
                    stop_time = ((t.hour + int(holdtime)) % 24) * 60 + t.minute
                    stop_time /= 15
                    self.change_request["CoolNextPeriod"] = stop_time
                    self.change_request["HeatNextPeriod"] = stop_time
        else:
            self.change_request["HeatNextPeriod"] = None
            self.change_request["CoolNextPeriod"] = None

    def temp(self, holdmode=None, holdtime=None, cool=None, heat=None):

        self.hold(holdmode, holdtime)

        if heat is not None:
            self.change_request["HeatSetpoint"] = int(heat)
        else:
            self.change_request["HeatSetpoint"] = None

        if cool is not None:
            self.change_request["CoolSetpoint"] = int(cool)
        else:
            self.change_request["CoolSetpoint"] = None

    def fan(self, mode=None):
        """
        Sets the request for fan as on or auto
        """
        if mode == Fan.ON:
            self.change_request["FanMode"] = Fan.ON
        elif mode == Fan.AUTO:
            self.change_request["FanMode"] = Fan.AUTO
        elif mode == Fan.CIRCULATE:
            self.change_request["FanMode"] = Fan.CIRCULATE
        elif mode == Fan.FOLLOWSCHEDULE:
            self.change_request["FanMode"] = Fan.FOLLOWSCHEDULE
        else:
            return False

        return self.change_request["FanMode"]

    def system(self, mode=None):
        """
        Sets the System Switch state
        """
        if mode == System.AUTO:
            self.change_request["SystemSwitch"] = System.AUTO
        elif mode == System.COOL:
            self.change_request["SystemSwitch"] = System.COOL
        elif mode == System.HEAT:
            self.change_request["SystemSwitch"] = System.HEAT
        elif mode == System.OFF:
            self.change_request["SystemSwitch"] = System.OFF
        else:
            return False
        return self.change_request["SystemSwitch"]

    def logout(self):
        """
        Logs out of the Honeywell site
        """
        response = ""
        if self.DEBUG > 0:
            print (">logout()")
        if self.valid_login:
            response = requests.get(self.BASEURL + "/Account/LogOff")
        self.valid_login = False
        if self.DEBUG > 0:
            print ("<logout()")
        return response

    # noinspection PyMethodMayBeStatic
    def period2time(self, period):
        """
        Translate 15 min periods sense midnight to time
        """
        hour = str(int(period * 15 / 60))
        if int(hour) > 12:
            hour = str(int(hour) - 12)
            ampm = "pm"
        else:
            ampm = "am"
        mintime = str(int(period) * 15 % 60).zfill(2)
        return hour + ":" + mintime + ampm
