#!/usr/bin/env python

import subprocess
import re
from subprocess import Popen, PIPE
from threading import Timer

sourcename="comm_speed.c"
exename="comm_speed"

mpicccommand=["mpicc","-Wl,-wrap,MPI_Recv","-Wl,-wrap,MPI_Finalize", sourcename, "some_test_helpers.c","-o",exename]
print "Compiling your "+sourcename+" file ...."
print " ".join(mpicccommand)
subprocess.call(mpicccommand)
print "Done."


num_procs=[2,4,6];
num_tests=[10,100,15];
test_size_MB=[1,30,2];


for testno in range(len(num_procs)):
    mpicommand=["mpirun","-np",str(num_procs[testno]),"./"+exename,str(test_size_MB[testno]),str(num_tests[testno])]
    
    print "Using the command: "+" ".join(mpicommand)

    print "\n\n\n\n\n"


    P=Popen(mpicommand,stdin=PIPE,stdout=PIPE,stderr=PIPE,bufsize=0)

    timer=Timer(30,lambda p:p.kill(),[P])
    timer.start()

    P.wait();
    [s1,s2]=P.communicate();
    if timer.isAlive():
        timer.cancel()
    else:
        print "It looks like this code entered an infinite loop, or was stuck waiting for input, or just refused to exit.  I had to kill it manually. "
        print "This code is not acceptable"
        exit()

    print "Here is the output of your program:"
    print s1
    print s2

    trans_rates=[x.split(':')[1].lower() for x in s1.split('\n') if 'rate' in x.lower() ]
    trans_rates=map(float,[re.findall('\d+.\d+',x)[0] for x in trans_rates])

    #Launch the standard code
    print "Launching the standard code to measure against"
    mpicommand=["mpirun","-np",str(num_procs[testno]),"comm_speed_standard",str(test_size_MB[testno]),str(num_tests[testno])]
    
    print "Using the command: "+" ".join(mpicommand)

    print "\n\n\n\n\n"
    P=Popen(mpicommand,stdin=PIPE,stdout=PIPE,stderr=PIPE,bufsize=0)
    P.wait();
    [s1,s2]=P.communicate();
    print "Here is the output of the standard code:\n"
    print s1
    print s2
    
    trans_rates_standard=[x.split(':')[1].lower() for x in s1.split('\n') if 'rate' in x.lower() ]
    trans_rates_standard=map(float,[re.findall('\d+.\d+',x)[0] for x in trans_rates_standard])

    max_measured_speed=max(trans_rates_standard)*8;
    min_measured_speed=min(trans_rates_standard)*0.125;

    out_of_range=[x for x in trans_rates if x<min_measured_speed or x>max_measured_speed];

    for rate in out_of_range:
        print "Your measurement of "+str(rate)+" MB/S is not reasonable.  The reasonable range is "+str(min_measured_speed)+" MB/S to "+str(max_measured_speed)+" MB/S"
        print "This code is not acceptable"
        exit();
        
    total_B_expected=test_size_MB[testno]*1024*1024*num_tests[testno]
    for i in range(1,num_procs[testno]):
        lines=open("whatidid.rank."+str(i)).readlines();
        lines=[l.split() for l in lines[1:]];
        if len(lines) < num_tests[testno]-3 or len(lines)>num_tests[testno]+3:
            print "Error, rank "+str(i)+" should have done between "+str(num_tests[testno]-3)+" and "+str(num_tests[testno]+3)+" recieves, but it did "+str(len(lines))
            print "This code is not acceptable"
            exit()
        total_B_recieved=sum([int(l[3]) for l in lines]);
        if  total_B_recieved<total_B_expected*0.99 or total_B_recieved>total_B_expected*1.01:
            print "Error, rank "+str(i)+" should have recieved "+str(total_B_expected)+" bytes in total, but actually recieved "+ str(total_B_recieved)
            print "The code is not acceptable"
            exit()
       
print "The code is now acceptable"       
