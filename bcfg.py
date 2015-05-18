from scipy import *;
from scipy.special import *;
#from numpy import matrix
from numpy import *
import sys
import string
import pylab, pickle
import numpy
import scipy
from math import ceil
from scipy.linalg import inv, det, eig
from math import *
from scipy.optimize import fmin_bfgs
from scipy.optimize import fmin_cg
from scipy.optimize import fmin_ncg
from model2 import*
from scipy import weave

"modify the bcfg


""" 
Perform logistic regression using BCFG (Quasi Netwton)
to estimate the parameters.
"""

def dlike(x,A,AC,imps,lam):
    x = asarray(x)
    grad1 = zeros(x.shape)
    w = exp(A*x)
    #number of observations
    m = A.shape[0];
    #number of variables not including intercept
    n = A.shape[1]-1;
    #i will take the gradient in two steps
    #ll1 = "w/(1.0+w)"
    #weave.blitz(ll1, check_size=0)
    ll = w/(1.0+w)
    ll = imps*ll
    ll = A.T*ll
    grad1 = (AC + ll)/float(m)
    grad2 = (2*lam*x[1:,])/float(n)
    grad1[1:,] = grad1[1:,] +grad2
    return  grad1 

#this function  computes the negative log likelihood of the data 
def like(x,A,AC,imps,lam):
    x = asarray(x)
    w = exp(A*x)
    m = float(A.shape[0]);
    n = float(A.shape[1]-1);
    f1 =  (lam/n)*dot(x[1:,].T,x[1:,])
    f = (dot(AC.T,x) + sum(imps*log(1.0+w)))/m + (lam/n)*dot(x[1:,].T,x[1:,])
    print f,f1 
    return f


#This function computes the Hessian
def hess(x,A,AC,imps,lam):
    x = asarray(x)
    w = exp(A*x)
    numobs = A.shape[0]
    numcol = A.shape[1]
    w2 = w/(1+w)**2
    H1 = sparse.lil_matrix((numobs,numobs))
    H1.setdiag(imps*w2)
    #print H1
    H2 = A.T * H1 *A
    #print "H2 is ",H2
    v1 = ones(numcol)
    v1[0] = 0
    v1 = lam/float(numcol)*v1
    H1 = sparse.lil_matrix((numcol,numcol))
    H1.setdiag(v1)
    #print "H1 is ",H1
    H3 = H2 +H1
    H3 = H3.todense()
    #print H3
    return H3

#this function computes the Hessian which is used in computing standard error

def myse(x,A,AC,imps):
    x = asarray(x)
    w = exp(A*x)
    numobs = A.shape[0]
    numcol = A.shape[1]
    w2 = w/(1+w)**2
    H1 = sparse.lil_matrix((numobs,numobs))
    H1.setdiag(imps*w2)
    H2 = A.T * H1 *A
    v1 = ones(numcol)
    v1[0] = 0
    v1 = lam/float(numcol)*v1
    H1 = sparse.lil_matrix((numcol,numcol))
    H1.setdiag(v1)
    H3 = H2 +H1
    H3 = H3.todense()
    H3 = inv(H3)
    print "------- doneeeeeeeeeeeee  -----------------"
    for ii in range(H2.shape[0]):
       bb = H3[ii,ii]
       print bb
    print "------- doneeeeeeeeeeeee  -----------------"
    return H3


"""
Predict the CTR 
"""
def predict(x,A,AC,imps,clicks):
    numobs = A.shape[0]
    numcol = A.shape[1]
    x = asarray(x)
    w = exp(A*x)
    numobs = A.shape[0]
    numcol = A.shape[1]
    w2 = w/(1+w)
    for ii in range(numobs):
        myimps = imps[ii,ii]
        myclicks = clicks[ii]
        print w2[ii] ,myimps,myclicks
    



#This function reads the names of the variables and
#stores them in a key 
def readBetaVector(filename):
          f = open(filename, "r")
          Betas = {}
          #loop over all the elements in the
          for line in f:
            ll = string.split(line)
            #Betas[str(ll[0])] = int(ll[1])
            Betas[int(ll[1])] =str(ll[0])
          f.close()
          return Betas



def readvec(filename,Beta):
          print filename
          f = open(filename,"r")
          for line in f:
            line = line.rstrip('\n')
            print line
            #ll = string.split(line)
            Beta.append(float(line))
          f.close()
          

DENSE_FLAG = False;
SPLIT_FLAG = False;
SPLITT = 100
x0 = zeros(2)

[A, clicks, imps] =  LoadDesign("us_x", "us_b",DENSE_FLAG,SPLIT_FLAG,SPLITT)
print "done with load"
#[A, clicks, imps] =  LoadDesign("test_x", "test_b",DENSE_FLAG,SPLIT_FLAG,SPLITT)
print A.shape
print clicks.shape
AC = -A.T*clicks
#x0 = rand(A.shape[1])
x0 = zeros(A.shape[1])
#we know that the CTR are within a certain range, set that 
#equal to the intercept
init = 3.0/1000.0
myp = log(init/(1.0-init))
x0[1] = myp
print myp
lam = 000.0 
a = like(x0,A,AC,imps,lam)

mvar = readBetaVector("varfile")


#xopt = fmin_bfgs(like, x0, fprime=dlike, full_output = 0, disp = 1 ,gtol=0.01,args=(A,AC,imps,lam))
xopt = fmin_cg(like, x0, fprime=dlike, full_output = 0, disp = 1 ,gtol=0.01,args=(A,AC,imps,lam))
#xopt = fmin_ncg(like, x0, fprime=dlike,fhess = hess,args=(A,AC,imps,lam),avextol=1.0e-8,full_output = 0, disp = 1)
print xopt
final = like(xopt,A,AC,imps,lam)
print xopt.shape[0]
#se = myse(xopt,A,AC,imps)
#the first vaibale is the intercept
#print "intercpt ", xopt[0], sqrt(se[0,0])
print "intercpt ", xopt[0]
for ii in range(xopt.shape[0]-1) :
    #get the varibale name
    myname = mvar[ii]
    myindex = ii+1
    #print  myname , " ", xopt[ii+1],ii, sqrt(se[myindex,myindex])
    print  myname , " ", xopt[ii+1],ii

#predict(xopt,A,AC,imps,clicks)


