#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import MySQLdb as mdb
from config import Database

try:
    dbcon = mdb.connect(Database["URL"], Database["User"], Database["Password"], Database["Database"])

    dbcon.query("SELECT VERSION()")
    assert isinstance(dbcon, object)
    result = dbcon.use_result()
    print ("MySQL version: %s" % result.fetch_row()[0])

#    dbcon.free_result()
#    c = dbcon.cursor()
#    c.execute("INSERT INTO mh_thermostat(CoolSetpoint) VALUES(55)")
#    dbcon.commit()
    
except mdb.Error, e:
    print "Error %d: %s" % (e.args[0], e.args[1])
    sys.exit(1)

finally:
    if dbcon:
        dbcon.close()
