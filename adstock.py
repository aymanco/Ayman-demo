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
cursor2 = db.cursor()


# Prepare SQL query to INSERT a record into the database.
sql = "SELECT distinct(OrderId) FROM goodorder" 
sql2 = "SELECT networkName FROM goodorder where OrderId =%s order by positionDatetime" 
try:
   # Execute the SQL command
   cursor.execute(sql)
   # Fetch all the rows in a list of lists.
   results = cursor.fetchall()
   for row in results:
      myid = row[0]
      myid =myid.strip()
      #now get the network name
      cursor2.execute(sql2,(myid,))
      myarray = []
      results2 = cursor2.fetchall()
      for row2 in results2:
      	mynetwork = row2[0]
        goodkey="other"
        if mynetwork in netdict:
       	 goodkey= netdict[mynetwork]
        myarray.append(goodkey) 
        #when we get here, print the array
      printarray( myid, myarray)
      #printarray(myid,myarray)
except:
   print "Error: unable to fecth data"

# disconnect from server
db.close()





