import requests
import datetime
import time

#currently queries only

username=''
password=''
deviceid=str()

auth={
    'timeOffset':240,
    'UserName':username,
    'Password':password,
    'RememberMe':'false'
    }

headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0',
    'Host': 'rs.alarmnet.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://rs.alarmnet.com/TotalConnectComfort'


    }
headers2 = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:31.0) Gecko/20100101 Firefox/31.0',
    'Host': 'rs.alarmnet.com',
    "Referer":"https://rs.alarmnet.com/TotalConnectComfort/Device/Control/"+deviceid,
    "X-Requested-With":"XMLHttpRequest",
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    }



s=requests.Session()

t = datetime.datetime.now()
utc_seconds = (time.mktime(t.timetuple()))
utc_seconds = int(utc_seconds*1000)

#login
r=s.post('https://rs.alarmnet.com/TotalConnectComfort',params=auth,headers=headers)
r.raise_for_status()


#validate
r=s.get('https://rs.alarmnet.com/TotalConnectComfort/Device/Control/'+deviceid,headers=headers)
r.raise_for_status()

#get device status
r=s.get('https://rs.alarmnet.com/TotalConnectComfort/Device/CheckDataSession/'+deviceid+'?_='+str(utc_seconds),headers=headers2)

#print "request headers"
#print r.request.headers
#print "response headers"
#print r.headers
#print "cookies"
#print r.cookies
#print r.text
#print r.status_code
r.raise_for_status()
print r.json()
