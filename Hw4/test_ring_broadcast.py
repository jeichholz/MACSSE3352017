#!/usr/bin/env python

import subprocess
from subprocess import Popen, PIPE
from threading import Timer

sourcename="ring_broadcast.c"
exename="ring_broadcast"

mpicccommand=["mpicc","-Wl,-wrap,MPI_Recv","-Wl,-wrap,MPI_Finalize", sourcename, "some_test_helpers.c","-o",exename]
print "Compiling your "+sourcename+" file ...."
print " ".join(mpicccommand)
subprocess.call(mpicccommand)
print "Done."

data=[4,5,0,9,44,-6];

num_procs=9

mpicommand=["mpirun","-np",str(num_procs),"./"+exename];
print "Using the command: "+" ".join(mpicommand)

print "Testing by inputting "+" followed by ".join(map(str,data))
print "\n\n\n\n\n"


P=Popen(mpicommand,stdin=PIPE,stdout=PIPE,stderr=PIPE,bufsize=0)

timer=Timer(5,lambda p:p.kill(),[P])

timer.start()
[s1,s2]=P.communicate(input='\n'.join(map(str,data))+'\n');
if timer.isAlive():
    print "Ok, no timeout"
    timer.cancel()
else:
    print "It looks like this code entered an infinite loop, or was stuck waiting for input, or just refused to exit.  I had to kill it manually. "
    print "This code is not acceptable"
    exit()

print s1
print s2

result=[1 for x in range(num_procs)];
for i in range(1,num_procs):
    R=open("whatidid.rank."+str(i)).readlines();
    R=R[1:];
    if len(R) != len(data):
       print "Error, rank "+str(i)+" should have done "+str(len(data))+" recieves, but it did "+str(len(R))
       result[i]=0
    for j in range(len(data)):
    	actual=map(int,R[j].split())[:-1]
    	if actual!=[j,i-1,data[j]]:
	   result[i]=0
	   print "Error, on rank "+str(i)+" the "+str(j)+"th recieve should come from rank 0 and contain data "+str(data[j])
	   print "However, it was from rank "+str(actual[1])+" and contained data "+str(actual[2])
    
if all(result):
   print "The code is now acceptable"
else:
   print "The code is not acceptable"   	

