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
tsql1 = "SELECT sum(conv) as totalconv FROM adstock where Id =%s and daynumber =%s" 

#This statement gets  the number of impressions the user has seen from a line on specific date 
tsql2 = "SELECT sum(imps) as totalimps  FROM adstock where Id =%s and daynumber=%s and lineid=%s " 

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
sql = "SELECT distinct(lineid) FROM adstock" 
linearray = []
cursor5.execute(sql)
lineresults = cursor5.fetchall()
for row in lineresults:
      myline = row[0]
      linearray.append(myline)



# Prepare SQL query to INSERT a record into the database.
sql = "SELECT distinct(Id) FROM adstock " 
#This statement checks whether they converted
sql2 = "SELECT conv FROM adstock where Id =%s order by mydate desc limit 1" 

#This statement gets the last  day i have seen the consumer 
sql3 = "SELECT max(daynumber)  as lastdate FROM adstock where Id =%s " 

#This statement gets the last  first  i have seen the consumer 
sql4 = "SELECT min(daynumber)  as firstdate FROM adstock where Id =%s " 


#THIS IS WINDOW NUMBER OF DAYS TO GO BACK
WINDOW = 7


# Generate the header automtically 
numberlines =len(linearray) 
myhead ="user,mytime,myconv,"
for ii in range(numberlines) :
    for jj in range(WINDOW) :
        thisad = "ad"+str(ii)+str(jj)
        myhead =myhead+","+thisad

print myhead
try:
   # Execute the SQL command
   cursor.execute(sql)
   # Fetch all the rows in a list of lists.
   results = cursor.fetchall()
   for row in results:
      myid = row[0]
      cursor2.execute(sql2,(myid,))
      results2 = cursor2.fetchone()
      isconverted = results2['conv']
      #get the first and last date we have seen the user
      cursor3.execute(sql3,(myid,))
      results3 = cursor3.fetchone()
      lastdate = results3['lastdate']
      
      cursor4.execute(sql4,(myid,))
      results4 = cursor4.fetchone()
      firstdate = results4['firstdate']
      #if the consumer has not converted
      #   1) we subsample
      #   2) They have Adstock beyond the last impression 
      if (isconverted ==1) :
        if (random.random() < 0.4 ):
      		generatehistory( db, myid, firstdate, lastdate, linearray,WINDOW)
      else:
        if (random.random() < 0.11):
      		generatehistory( db, myid, firstdate, lastdate, linearray,WINDOW)
except:
   print "Error: unable to fecth data"

# disconnect from server
db.close()





