#!/usr/bin/env python

import subprocess
from subprocess import Popen, PIPE
from threading import Timer
import os, glob
from math import *
import random
import sys
import time


sourcename="eratosthenes"
sourcefiles=[sourcename+".c"]
helper_sourcefiles=['eratosthenes_test_helpers.c']
flags=['--std=c99','-g','-lm','-Wall']
wrapped_functions=['MPI_Init','MPI_Finalize','MPI_Send'];
exename='./'+sourcename
default_timeout=30

RED='\033[91m'
GREEN='\033[92m'
ENDC='\033[0m'

def fail():
    print "This code is "+RED+" not acceptable"+ENDC
    exit(1)

def succeed():
    print "This code is "+GREEN+"acceptable"+ENDC
    exit(0)

def ref_dir():
    d="./"
    for a in sys.argv[1:]:
        if a[:12]!='--max-procs=':
            d=sys.argv[1]+'/'
    return d;

def run_command(command="",abort_on_failure=True,abort_on_timeout=True,timeout_returncode=-2,print_command=True,print_output=False,timeout=default_timeout):
    if print_command:
        print "Executing command:"
        print " ".join(command)
    P=Popen(command,stdin=PIPE,stdout=PIPE,stderr=PIPE)
    timer=Timer(timeout,lambda p:p.kill(),[P])
    timer.daemon=True;
    timer.start()
    P.wait()
    [s1,s2]=P.communicate();
    if timer.isAlive():
        timer.cancel()
    else:
        if abort_on_timeout:
            print "It looks like this code entered an infinite loop, or was stuck waiting for input, or just refused to exit.  I had to kill it manually. "
            fail()
        else:
            returncode=timeout_returncode
    if P.returncode != 0 and abort_on_failure:
        print s1
        print s2
        print "Error.  The return code was non-zero, meaning that this code crashed."
        fail()
    returncode=P.returncode

    if print_output:
        print s1
        print s2
    return returncode,s1,s2

def run_instance(standard,np=3,print_results=None,make_outputfile=True,N=50,deep_log=False,timeout=default_timeout,print_output=True):
    if not standard:
        for f in glob.glob('whatidid.*'):
            os.remove(f)
    if standard==False:
        command=['mpirun','-np',str(np),exename]
    else:
        command=['mpirun','-np',str(np),ref_dir()+exename+'_standard']
    if print_results is not None:
        command=command+['--print_results='+str(print_results)];
    if standard and make_outputfile:
        command=command+['--output_file=primelist_standard.txt']
    if not standard and make_outputfile:
        command=command+['--output_file=primelist.txt']
    if deep_log:
        command=command+['--deep-log']
    command=command+[str(N)]

    returncode,s1,s2=run_command(command,print_output=print_output,timeout=timeout)
    return returncode,s1,s2


def multiple_of(x,divisors):
    return any([x % y == 0 for y in divisors])


def primes_up_to(n):
    L=[1 for i in range(0,n+1)];
    L[0]=0;
    L[1]=0;
    p=0;
    while p**2<=n:
        p+=1
        while L[p]==0 and p**2<=n:
            p+=1
        idx=2*p;
        while idx<=n:
            L[idx]=0;
            idx+=p;
    return [i for i in range(0,n+1) if L[i]==1]
    


def check_output_correctness(s1,standard_s1,checkfiles=False):
    retrieve_list_from_output=lambda s: [int(l) for l in s.split('\n') if len(l)>0 and l.isdigit()]
    s1_numbers=retrieve_list_from_output(s1)
    s1_standard_numbers=retrieve_list_from_output(standard_s1)

    if s1_numbers != s1_standard_numbers:
        print "Error, at least one of your results that got printed to the terminal is incorrect.  Try running your code and the standard code using the commands listed above, and see what the difference is. I'm looking at every single line that contains only numbers, and I am looking at order."
        fail()

    if checkfiles:
        s1_numbers=open('primelist.txt','r').readlines();
        s1_standard_numbers=open('primelist_standard.txt','r').readlines();
        if s1_numbers != s1_standard_numbers:
            print "Error, at load one of your results that got printed to the output file is incorrect. Compare primeslist.txt and primeslist_standard.txt to see what the problem is."
            fail()

def main(argv):
    
    if len(argv)>1:
        if argv[1][:12]=='--max-procs=':
            max_procs=int(argv[1][12:])
        else:
            print "Error, option "+argv[1]+" not recognized."
            exit()
    else:
         max_procs=180

    mpicccommand=["mpicc"]+flags+map(lambda x:'-Wl,-wrap,'+x,wrapped_functions)+sourcefiles+map(lambda x:ref_dir()+x,helper_sourcefiles)+["-o",exename]
    gcc_status=run_command(mpicccommand,timeout=2)[0];
    if gcc_status != 0:
        print "Error, gcc either had warnings or the code completely failed to compile.  Fix these things before proceeding.  The compiler is your friend, and is trying to help you."
        fail()

    width=100
    #Test a couple random cases, test whether or not hte code respects the --print parameter.
    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False);
    dummy,s1_stand,s2_stand=run_instance(standard=True)
    check_output_correctness(s1,s1_stand)

    # Test a couple random cases, test whether or not hte code respects the --print parameter.
    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False,make_outputfile=True);
    dummy,s1_stand,s2_stand=run_instance(standard=True,make_outputfile=True)
    check_output_correctness(s1,s1_stand,checkfiles=True)

    #No output, long list, check the output files.
    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False,make_outputfile=True,N=500,np=1);
    dummy,s1_stand,s2_stand=run_instance(standard=True,make_outputfile=True,N=500,np=1)
    check_output_correctness(s1,s1_stand,checkfiles=True)    

    #No output, long list, check the output files.
    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False,make_outputfile=True,N=500,np=2);
    dummy,s1_stand,s2_stand=run_instance(standard=True,make_outputfile=True,N=500,np=2)
    check_output_correctness(s1,s1_stand,checkfiles=True)    

    #No output, long list, check the output files.
    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False,make_outputfile=True,N=500,np=3);
    dummy,s1_stand,s2_stand=run_instance(standard=True,make_outputfile=True,N=500,np=3)
    check_output_correctness(s1,s1_stand,checkfiles=True)    

    #No output, long list, check the output files.
    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False,make_outputfile=True,N=500,np=7);
    dummy,s1_stand,s2_stand=run_instance(standard=True,make_outputfile=True,N=500,np=7)
    check_output_correctness(s1,s1_stand,checkfiles=True)    

    #No output, long list, check the output files.
    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False,make_outputfile=True,N=500,np=13);
    dummy,s1_stand,s2_stand=run_instance(standard=True,make_outputfile=True,N=500,np=13)
    check_output_correctness(s1,s1_stand,checkfiles=True)   

    #Now make sure that the pipelining is working correctly
    NP=[4,4,4,2,3];
    P=[4,8,32,200,3000];
    primeslist=primes_up_to(40000);
    for np,p in zip(NP,P):
        print "".join(['=' for i in range(width)]);
        dummy,s1,s2=run_instance(standard=False,make_outputfile=True,N=p,np=np,deep_log=True);
        for rank in range(np):
            send_partners=lambda f: [int(l.strip().split(':')[1].split()[0]) for l in open(f).readlines()]
            #Processors should only send to the next rank, or maybe rank 0.
            if any([s != rank+1 and s!=0 for s in send_partners('whatidid.rank.'+str(rank)+'.txt')[:-1]]):
                print "Error, somewhere along the way rank "+str(rank)+" sent to a processor other than "+str(rank+1)+" or 0.  You aren't pipelining at that point."
                fail()
            send_sizes=lambda f: [int(l.strip().split(':')[1].split()[2]) for l in open(f).readlines()]
            if any([d!=1 and d!=0 for d in send_sizes('whatidid.rank.'+str(rank)+'.txt')[:-1]]):
                print "This is supposed to be a very classic pipelining algorithm -- send only one piece of data at a time.  Rank "+str(rank)+" sent a non-zero and non-one amount of data somewhere."
                fail()
            myprimes=primeslist[rank*(p/np):(rank+1)*(p/np)]
            send_data=lambda f: [int(l.strip().split(':')[1].split()[1]) for l in open(f).readlines()]
  
            S=send_data('whatidid.rank.'+str(rank)+'.txt')[:-1]
            for s in S:
                if s>0 and multiple_of(s,myprimes):
                    print "Error. Rank "+str(rank)+" should end up being a filtering out all multiples of "+str(myprimes)+". However, it is forwarding "+str(s)+" at some point."
                    fail()


    #Big cases.
    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False,make_outputfile=True,N=50000,np=27,timeout=120);
    dummy,s1_stand,s2_stand=run_instance(standard=True,make_outputfile=True,N=50000,np=27,timeout=120)
    check_output_correctness(s1,s1_stand,checkfiles=True)  
                    
    succeed()


if __name__=='__main__':
    main(sys.argv)
