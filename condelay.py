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

tcursor1 = db.cursor(MySQLdb.cursors.DictCursor)
tcursor2 = db.cursor(MySQLdb.cursors.DictCursor)

#This statement checks if the user had a conversion on that date 
tsql1 = "SELECT sum(conv) as totalconv FROM sadstock where Id =%s and daynumber =%s" 

#This statement gets  the number of impressions the user has seen from a line on specific date 
tsql2 = "SELECT sum(imps) as totalimps  FROM sadstock where Id =%s and daynumber=%s and lineid=%s " 

def generatehistory( db, myid, firstdate, lastdate, myarray,WINDOW):
        #get day range
        myrange = lastdate -firstdate
        for day in range(myrange+1):
            aday = firstdate+day
            mystring =str(myid)+","+ str(aday)
            tcursor2.execute(tsql1,(myid,aday))
	    convresults = tcursor2.fetchone()
            myconv = 0
            convcount = convresults['totalconv']
            if convcount != None :
                   	myconv = convcount 
                        myconv = min(myconv,1)
            #add the conversion to the string
            mystring = mystring+","+str(myconv)
           
            #this is the total imps in history
            totalimps = 0
	    for lineitem in linearray:
                # we now go back a window of days
                for goback in range(WINDOW) :
                        theday = aday -goback
                	tcursor1.execute(tsql2,(myid,theday,lineitem))
			impresults = tcursor1.fetchone()
                	mycount = 0
                	impcount = impresults['totalimps']
                	if impcount != None :
                   		mycount = impcount
                	#print "The count ",aday, theday, lineitem, myid,mycount 
                        totalimps = totalimps+mycount
                        mystring = mystring+","+str(mycount)
            if ( totalimps > 0) :
            	print mystring




# prepare a cursor object using cursor() method
cursor = db.cursor()
cursor2 = db.cursor(MySQLdb.cursors.DictCursor)
cursor3 = db.cursor(MySQLdb.cursors.DictCursor)
cursor4 = db.cursor(MySQLdb.cursors.DictCursor)
cursor5 = db.cursor()

#create an array of all the Line items that we have
sql = "SELECT distinct(lineid) FROM sadstock" 
linearray = []
cursor5.execute(sql)
lineresults = cursor5.fetchall()
for row in lineresults:
      myline = row[0]
      linearray.append(myline)



# Prepare SQL query to INSERT a record into the database.
sql = "SELECT distinct(Id) FROM sadstock where conv = 1  " 
#This statement checks whether they converted
sql2 = "SELECT daynumber FROM sadstock where Id =%s order by daynumber desc limit 2" 




try:
   # Execute the SQL command
   cursor.execute(sql)
   # Fetch all the rows in a list of lists.
   results = cursor.fetchall()
   for row in results:
      myid = row[0]
      cursor2.execute(sql2,(myid,))
      results2 = cursor2.fetchone()
      convtime = results2['daynumber']
      #get the time of last impression 
      results2 = cursor2.fetchone()
      imptime = results2['daynumber']
      delay = convtime-imptime
      print myid, convtime, imptime, delay

except:
   print "Error: unable to fecth data"

# disconnect from server
db.close()





