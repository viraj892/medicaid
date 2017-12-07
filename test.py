import cx_Oracle
import mysql.connector
import datetime
import csv
import sys
import re
import string
import itertools
import os

print datetime.datetime.now()

logic = {}

con = mysql.connector.connect(user='root', password='ncsuball', host='127.0.0.1', database='medicaid')
cursor = con.cursor()

querystring = ("SELECT * FROM test WHERE `id` = 1")
cursor.execute(querystring)

field_names = [d[0].lower() for d in cursor.description]
rows = cursor.fetchmany()
for row in rows:
        logic.update(dict(itertools.izip(field_names, row)))

a = 'y'

exec(logic['code'])

#~ if a == 'y':
        #~ print 'boom'