#!/usr/bin/env python

import subprocess
from subprocess import Popen, PIPE
from threading import Timer
import os, glob
from math import *
import random
import sys
import time


sourcename="linear_solve"
sourcefiles=[sourcename+".c"]
helper_sourcefiles=['linear_solve_test_helpers.c']
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

def run_instance(standard,np=3,print_results=None,dim=3,deep_log=False,timeout=default_timeout,print_output=True):
    if not standard:
        for f in glob.glob('whatidid.*'):
            os.remove(f)
    if standard==False:
        command=['mpirun','-np',str(np),exename]
    else:
        command=['mpirun','-np',str(np),ref_dir()+exename+'_standard']
    if print_results is not None:
        command=command+['--print_results='+str(print_results)];
    if standard:
        command=command+['x=x_standard.txt']
    if not standard:
        command=command+['x=x.txt']
    if deep_log:
        command=command+['--deep-log']

    command=command+['A=A'+str(dim)+'.txt']
    command=command+['b=b'+str(dim)+'.txt']

    command=command+['--produce_file']
    returncode,s1,s2=run_command(command,print_output=print_output,timeout=timeout)
    return returncode,s1,s2

def check_output_correctness():
    extract_vector=lambda f: map(float,open(f).readlines()[1:])
    x=extract_vector('x.txt');
    x_standard=extract_vector('x_standard.txt');
 

    if (len(x)!=len(x_standard)):
        print "Error! the vector x and the vector x_standard are different dimensions.  Your x is "+str(len(x))+" long while x_standard is "+str(len(x_standard))+" long."
        fail()

    if (any([abs(x[i]-x_standard[i])>1e-6 for i in range(len(x))])):
        print "Error, x and x standard vary by more than 10^-6 in at least one position.  Check out x.txt and x_standard.txt"
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
    check_output_correctness()

    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False,dim=10);
    dummy,s1_stand,s2_stand=run_instance(standard=True,dim=10)
    check_output_correctness()    

    for np in [1,2,3,4,5,6,10]:
        print "".join(['=' for i in range(width)]);
        dummy,s1,s2=run_instance(standard=False,dim=10,np=np);
        dummy,s1_stand,s2_stand=run_instance(standard=True,dim=10,np=np)
        check_output_correctness()   
        

    for np in [1, 2, 3, 4, 5, 6]:
        dummy,s1,s2=run_instance(standard=False,dim=60,deep_log=True,np=np);
        for rank in range(np):
            send_partners=lambda f: [int(l.strip().split(':')[1].split()[0]) for l in open(f).readlines()]
            send_sizes=lambda f: [int(l.strip().split(':')[1].split()[1]) for l in open(f).readlines()]
            SP=send_partners('whatidid.rank.'+str(rank)+'.txt')
            SL=send_sizes('whatidid.rank.'+str(rank)+'.txt')
            if any([s != rank+1 and s!=rank-1 for s in SP]):
                print "Error.  This is a pipelining algorithm. Rank "+str(rank)+" should only communicate with rank "+str(rank-1)+" and rank "+str(rank+1)+".  However, that didn't happen here. "
                fail()
            total_data_sent_forward=sum([SL[i] for i in range(len(SP)) if SP[i]==rank+1]);
            num_sends_forward=len([x for x in SP if x==rank+1]);
            total_data_sent_backward=sum([SL[i] for i in range(len(SP)) if SP[i]==rank-1]);
            num_sends_backward=len([x for x in SP if x==rank-1]);
            chunksize=60/np;
            min_sends_forward=chunksize*(rank+1)
            if rank==np-1:
                min_sends_forward=0;
            max_sends_forward=chunksize*(rank+1)*3
            min_sends_backward=(np-rank)*chunksize;
            if rank==0:
                min_sends_backward=0;
            max_sends_backward=(np-rank)*chunksize*3;
            if num_sends_forward<min_sends_forward or num_sends_forward>max_sends_forward:
                print "Error. This is a pipelining algorithm, and rank "+str(rank)+" is responsible for "+str(chunksize)+" rows.  This rank should do at least "+str(min_sends_forward)+" and at most "+str(max_sends_forward)+" sends to the next rank.  However, it did "+str(num_sends_forward)
                fail()
            if num_sends_backward<min_sends_backward or num_sends_backward>max_sends_backward:
                print "Error.  This is a pipelining algorithm, and rank "+str(rank)+" is repsonsible for "+str(chunksize)+" rows.  During back substitution, this rank should do at least "+str(min_sends_backward)+" and at most "+str(max_sends_backward)+" sends to the previous rank.  However, it did "+str(num_sends_backward)
                fail()
            if total_data_sent_forward != 61*chunksize*(rank+1) and rank!=np-1:
                print "Error.  Rank "+str(rank)+" is repsonsible for "+str(chunksize)+" rows, plus the "+str(chunksize*(rank))+" previous rows.  The matrix is 60 columns wide, and there is 1 column for b.  Therefore, this rank should send "+str(61*chunksize*(rank+1))+" doubles to the next rank.  However, it sent "+str(total_data_sent_forward)
                fail()
            if total_data_sent_backward != chunksize*(np-rank) and rank!=0:
                print "Error.  Rank "+str(rank)+" is repsonsible for "+str(chunksize)+" rows, plus the "+str(chunksize*(np-rank-1))+" rows lower in the matrix. During back-substitution, this rank should send "+str(chunksize*(np-rank))+" doubles to the previous rank.  However, it sent "+str(total_data_sent_backward)
                fail()
        
    print "".join(['=' for i in range(width)]);
    dummy,s1,s2=run_instance(standard=False,dim=2520,np=30);
    dummy,s1_stand,s2_stand=run_instance(standard=True,dim=2520,np=30)
    check_output_correctness()    

    


    
                    
    succeed()


if __name__=='__main__':
    main(sys.argv)
