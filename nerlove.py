#!/usr/bin/python
"""
This module will Open the Mysql database and then 
for each user will generate the sequence of touch points
that the user

I want to write the data in the form 
Id,from,to,entry,exit

"""


import sys
import os
import MySQLdb
import string
import time
from time import strptime
import datetime
from math import *
import re
import random


# Open database connection
db = MySQLdb.connect("localhost","ayman","abobaker","deals" )



# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor2 = db.cursor(MySQLdb.cursors.DictCursor)
cursor3 = db.cursor(MySQLdb.cursors.DictCursor)
cursor4 = db.cursor(MySQLdb.cursors.DictCursor)
cursor5 = db.cursor()

# get the users who converted and have seen impressions on the day they converted 
sql = "select distinct(ID) from adstock2 where myconv = 0 and myimps > 0;  " 
#This statement checks whether they converted
sql2 = "select count(*)  as mycount  from adstock2 where ID = %s and  myconv =  0 and myimps > 0;" 

#This statement get the time of the impression  
sql3 ="select daynumber from adstock2 where ID = %s order by daynumber desc limit 3;"




try:
   # Execute the SQL command
   cursor.execute(sql)
   # Fetch all the rows in a list of lists.
   results = cursor.fetchall()
   for row in results:
      myid = row[0]
      cursor2.execute(sql2,(myid,))
      results2 = cursor2.fetchone()
      thecount = results2['mycount']
      if (thecount > 2) :
	#get the time of t-1, t-2 
        cursor3.execute(sql3,(myid,))
        t0 = cursor3.fetchone()
        time0 = t0['daynumber']
        t1 = cursor3.fetchone()
        time1 = t1['daynumber']
        t2 = cursor3.fetchone()
        time2 = t2['daynumber']
        #get the deltas 
        delta1 = float(time0-time1)
        delta2 = float(time1-time2)

        print delta1 , delta2

except:
   print "Error: unable to fecth data"

# disconnect from server
db.close()





