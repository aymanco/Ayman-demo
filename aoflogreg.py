# Figures 7.1, page 355.
# Logistic regression.

import pickle
from cvxopt import solvers, matrix, spdiag, log, exp, div
#solvers.options['show_progress'] = False
#try more changes


#Load the data from the text file and build the matrix of observations
filename ="gnome3.csv"
#read the first line  and get the number of entries and the dimension of the data 

f = open(filename, "r")
line = f.readline()
ll = line.split(',')
mydim =  int(ll[0])
numentry = int(ll[1])
A = matrix(1.0, (numentry, mydim+1))
y = matrix(1.0, (numentry,1))
counter = 0 
for line in f:
    ll = line.split(',') 
    print counter
    y[counter,0] = float(ll[0])
    for jj in range(len(ll)-1):
         myindex = jj+1
         print jj, myindex, counter
         A[counter, myindex] = log(float(ll[myindex])+1.0)
    counter = counter+1
f.close()



# minimize   sum_{y_k = 1} (a*uk + b) + sum log (1 + exp(a*u + b))
#
# two variables a, b. 

#A[:,0] = u

# I want to multiply everu element in u by Y and then sum across rows

c = -A.T*y



def F(x=None, z=None):
   #if x is None: return 0, matrix(0.0, (5,1))
   if x is None: return 0, matrix(0.0, (2,1))
   w = exp(A*x)
   f = c.T*x + sum(log(1+w))
   grad = c + A.T * div(w, 1+w)  
   if z is None: return f, grad.T
   H = A.T * spdiag(div(w,(1+w)**2)) * A
   return f, grad.T, z[0]*H 

# I will constrain the solution so that 
#  x1 > x2 > x3 > x4 > 0  
# I will require that say x1 > x2
G = matrix([[0. , -1., 1.0 , 0.0, 0.0] , [ 0.0,0.0, -1.0, 1.0, 0.0], [ 0. , 0 , 0, -1, 1.0] , [ 0. , 0. , 0. , 0., -1.0]])
#G = matrix([[0. , -1., 1.0 , 0.0, 0.0] , [ 0.0,0.0, -1.0, 1.0, 0.0], [ 0. , 0 , 0, -1, 1.0] ])
print G
G = G.T
H = matrix(0., (4, 1))
print G
print H
sol = solvers.cp(F)
#sol = solvers.cp(F, G, H)
a, b = sol['x'][0], sol['x'][1]
print  sol['x'] 

try: import pylab
except ImportError: pass
else:
    pylab.figure(facecolor='w')
    nopts = 200
    pts = -1.0 + 12.0/nopts * matrix(list(range(nopts))) 
    w = exp(a*pts + b)
    pylab.plot(u, y, 'o', pts, div(w, 1+w), '-')
    pylab.title('Logistic regression (fig. 7.1)')
    pylab.axis([-1, 11, -0.1, 1.1])
    pylab.xlabel('u')
    pylab.ylabel('Prob(y=1)')
    pylab.show()
