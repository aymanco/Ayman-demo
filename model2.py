#  Ayman Farahat 


import sys
import string
import pylab, pickle
from  numpy import *
from scipy import *
from math import ceil
from numpy import numarray



"""
read the Betas of a trained model and returns the result
in a Dictionary. The dictionary is used for prediction
"""
def readBetaVector(filename):
          f = open(filename, "r")
          Betas = {}
          #loop over all the elements in the
          for line in f:
            ll = string.split(line)
            Betas[str(ll[0])] = float(ll[1])
          f.close()
          return Betas 

def readWVector(filename):
          f = open(filename, "r")
          line = f.readline()
          #read the second line
          line = f.readline()
          ll = string.split(line)
          numentry = int(ll[0])
          #allocate matrix for I, J and V
          #loop over all the elements in the
          myv = zeros((numentry, 2))
          counter = 0
          for line in f:
            ll = string.split(line)
            myv[counter, 0] = float(ll[0])
            myv[counter, 1] = float(ll[1])
            counter = counter+1
          f.close()
          clicks = myv[:, 0]
          #imps = spmatrix(myv[:, 1], range(numentry), range(numentry))
          imps = sparse.lil_matrix((numentry,numentry))
          imps.setdiag(myv[:,1])
          return  clicks, imps ,myv[:,1]

def readVector(filename):
          f = open(filename, "r")
          line = f.readline()
          #read the second line
          line = f.readline()
          ll = string.split(line)
          numentry = int(ll[0])
          #allocate matrix for I, J and V
          #myv = matrix(0.0, (numentry, 1))
          myv = zeros((numentry, 1))
          #loop over all the elements in the
          counter = 0
          for line in f:
            ll = string.split(line)
            #set to 0 1 
            myv[counter] = float(ll[0])
            if ll[0] == -1 :
               myv[counter] =0.0 
            counter = counter+1
          f.close()
          return myv


def readDenseDesign(filename):
	try:
          f = open(filename, "r")
          line = f.readline()
          #read the second line
          line = f.readline()
          ll = string.split(line)
          L = len(ll)
          #the format is number_rows number_cols number_entries 
          #allocate matrix for I, J and V
          numrow = int(ll[0])
          numcol = int(ll[1])
          mymatrix = zeros((numrow, numcol))
          #loop over all the elements in the 
          counter = 0
          for line in f:
            #ll = string.split(line,",")
            ll = string.split(line)
            for j in range(numcol) :
              mymatrix[counter, j] = float(ll[j])
            counter = counter+1
          f.close()
          return mymatrix 
        except Exception, e:
          print "Invalid File"

def readDesign(filename):
	try:
          f = open(filename, "r")
          line = f.readline()
          #read the second line
          line = f.readline()
          ll = string.split(line)
          L = len(ll)
          #the format is number_rows number_cols number_entries 
          numrow = int(ll[0])
          #i will add the col for the intercept here
          numcol = int(ll[1])+1 
          mysparse = sparse.lil_matrix((numrow,numcol))
          counter = 0
          for line in f:
            ll = string.split(line)
            myrow = int(ll[0])
            mycol = int(ll[1])+1
            myvalue = float(ll[2])
            counter = counter+1
            mysparse[myrow,mycol] = myvalue
          f.close()
          #make a sparsematrix 
          return mysparse 
        except Exception, e:
          print "Invalid File"


def LoadDesign(designfile, impsfile,DenseFlag,SPLIT_FLAG,SPLITT):
   print impsfile
   #get the data from the sparse files
   [clicks, imps,vimps] = readWVector(impsfile)
   print "done here"
   if DenseFlag == False:
     u = readDesign(designfile)
   if DenseFlag == True:
     u = readDenseDesign(designfile)
   m = u.shape[1]
   #get the size of the data
   print "created matrix"
   #set the first col to all ones 
   u[:, 0] = ones(m) 
   print "all set"
   return u, clicks, imps




def aofmul(x=None, y=None) :
    mynumber = x.size[0]
    z = matrix(0.0, (mynumber, 1))
    #this is a hack becuase the CTR can be way off
    for i in range(mynumber):
      if (x[i] > 0.02):
        x[i] = 0.02
      z[i] = x[i]*y[i, i]
    return z


#define a function that computes the liklehood on the validation data
# and also compute the prediction error

def vFwrapper(vimps,vclicks,vA,vc,weights):
    vm = vA.size[0];
    vn = vA.size[1]-1;
    #for the constant part of the summation, do this off line
    #vc = -vA.T*vclicks;
    

    def vF(x=None):
       #print ("Vimps ",vimps.size[0],vimps.size[1])
       #note that the x vector is [ b u] and only b impacts the logistic function
       w = exp(vA*x[0:vn+1])
       f = (vc.T*x[0:vn+1] + sum(vimps*log(1+w)))
       #get the conversion rates 
       theta = spmatrix(div(w, (1.0+w)), range(vm), range(vm))
       theta = div(w, (1+w))
       pclicks = aofmul(theta, vimps) 
       #get predicted clicks
       return f, pclicks
    [f,pclicks] = vF(weights);
    return f,pclicks


#compute the logliklehood ratio 
# we are given n1 : number of trials of set 1
#              k1 : number of success of set 1
#              n2  : number of trials of set 2
#              k2  : number of trials of set 2
#  we return the liklehood score and the 
def llr(mat) :   
     myrow = mat.size[0]
     mycol = mat.size[1]
     bigN = sum(mat)
     lam = 0.0
     for i in range(mycol) :
        thiscol = mat[:,i] 
        ci = sum(thiscol)
        for j in range(myrow) :
          thisrow = mat[j,:] 
          rj = sum(thisrow)
          lam = lam+ 2.0*mat[j,i]*log((mat[j,i]*bigN)/(ci*rj))
     return lam 
            


# Standardize the martix to a transition matrix 
#  The sum of rows should be 1 
def totrans(mat) :   
     myrow = mat.size[0]
     mycol = mat.size[1]
     bigN = sum(mat)
     lam = 0.0
     for i in range(myrow) :
        thisrow = mat[i,:] 
        ri = sum(thisrow)
        if ri > 0.0 :
           for j in range(mycol) :
               mat[i,j] = mat[i,j] /ri
     return mat 
            



def matchrow(x=None,y=None) :
    mynumber = y.size[0]
    thismatch = -1
    for i in range(mynumber):
      ll = x-y[i,:]
      pp = abs(ll)
      pp1 = sum(pp)
      if pp1 == 0 :
         thismatch =i
    return thismatch

