#!/usr/bin/env python

import subprocess
import re
from subprocess import Popen, PIPE
from threading import Timer
import time
from math import pi

sourcename="estimate_pi.c"
exename="estimate_pi"

mpicccommand=["mpicc","-Wl,-wrap,srand","-Wl,-wrap,MPI_Finalize", "-Wl,-wrap,incircle", sourcename, "more_test_helpers.c","-o",exename]
print "Compiling your "+sourcename+" file ...."
print " ".join(mpicccommand)
subprocess.call(mpicccommand)
print "Done.\n\n"


num_procs=[2,10,20];
N=[10000,500,100000]

R=[100,100,100];

for testno in range(len(num_procs)):
    pi4_est=[];
    
    mpicommand=["mpirun","-np",str(num_procs[testno]),"./"+exename,str(N[testno])]
    print "Launching using the command: "+" ".join(mpicommand)
    print "Re-running your code "+str(R[testno])+" times"
    

    print "\n\n\n"

    for t in range(R[testno]):
        P=Popen(mpicommand,stdin=PIPE,stdout=PIPE,stderr=PIPE,bufsize=0)

        timer=Timer(60,lambda p:p.kill(),[P])
        timer.start()

        P.wait();
        [s1,s2]=P.communicate();
        if timer.isAlive():
            timer.cancel()
        else:
            print "It looks like this code entered an infinite loop, or was stuck waiting for input, or just refused to exit.  I had to kill it manually. "
            print "This code is not acceptable"
            exit()

        pi4_est.append(1.0/4*float(re.findall('\d\.\d+',s1)[0]));
        time.sleep(3)
        seeds=[]
        for procno in range(num_procs[testno]):
            lines=open("whatidid.rank."+str(procno),"r").readlines();
            seedtimes=int(lines[0].split(":")[1]);
            if seedtimes != 1:
                print "Error: Processor "+str(procno)+" should seed the random number generator exactly 1 time, but it seeded it "+str(seedtimes)+" times"
                print "This code is not acceptable"
                exit()
            seeds.append(int(lines[1].split(':')[1]));
            for k in range(len(seeds)):
                if seeds.count(seeds[k])>1:
                    print "Error.  More than one processor seeded the random number generator with the seed "+str(seeds[k])+".  This will produce biased samples."
                    print "This code is not acceptable"
                    exit()
            incircle=int(lines[2].split(':')[1]);
            if incircle != N[testno]:
                print "Error.  Processor "+str(procno)+" should have tested "+str(N[testno])+" samples, but it tested "+str(incircle)
                print "This code is not acceptable."
                exit()
        
    print "Estimates of pi/4:"
    print pi4_est
    theta_bar=sum(pi4_est)/len(pi4_est);
    print "theta bar="+str(theta_bar)
    ss=1.0/(len(pi4_est)-1)*sum([(theta-theta_bar)**2 for theta in pi4_est]);
    print "s^2="+str(ss)
    sigmasigma=pi/4*(1-pi/4)/(N[testno]*num_procs[testno]);
    print "sigma^2="+str(sigmasigma)
    T=(len(pi4_est)-1)*ss/sigmasigma;
    
    print "T="+str(T)
    if T>138.98:
        print "The variance in your estimates is much too high.  You are likely using too few samples"
        print "This code is not yet acceptable"
        exit()
    if T<65:
        print "The variance in your estimates is much too low.  You are likely using too many samples."
        print "This code is not yet acceptable"
        exit()
