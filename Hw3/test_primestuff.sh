#!/bin/bash


pname=primestuff

standard_dir='./'

num_testcases=7

timeout_len=5

overall_success=1

if [ $# > 1 ]
then
    standard_dir=$1
fi


function ifname()
{
    echo ${1}_input_${2}.txt
}

function ofname(){
    if [ $3 == 1 ]
    then
	echo ${1}_standard_output_${2}.txt
    else
	echo ${1}_output_${2}.txt
    fi
    
}


com[0]="--list 1 20"
com[1]="--list -1 0 1 2 3 4 5 6 7 8 9 10"
com[2]="--range 5 20"
com[3]="--range"
com[4]="--notanoption"
com[5]="--range 1"
com[6]="--range 1 500"

gcc  $pname.c -o $pname -lm

for testcase in `seq 0 $(($num_testcases-1))`
do
    echo
    echo "------------------"
    echo "Testing on input $testcase"
    echo "This test case is run using"
    echo "$pname ${com[$testcase]}"
    echo "The resulting output of each piece of code is found in $(ofname $pname $testcase 0)"
    echo "and $(ofname $pname $testcase 1)"
    echo "------------------"
    echo
    echo

    timeout $timeout_len ./$pname ${com[$testcase]} > "$(ofname $pname $testcase 0)"
    code_timeout=$?
    
    timeout $timeout_len ${standard_dir}/${pname}_standard ${com[$testcase]} > "$(ofname $pname $testcase 1)"


    if [ $code_timeout == 124 ]
    then
	echo "It looks like your code entered an infinite loop.  The testing code had to kill it."
	echo "It may have produced a lot of output because of that. "
	echo "I'm not going to display your output.  Check the file $(ofname $pname $testcase 0) for that"
	testoutcome=1
    fi

    if [ $code_timeout != 124 ]
    then
	diff -y -w "$(ofname $pname $testcase 0)" "$(ofname $pname $testcase 1)"
	testoutcome=$?
    fi

    echo
    echo
    if [ $testoutcome == 0 ]
    then
	echo "Test ${testcase} successful"
    else
	echo "Test ${testcase} unsuccessful"
	overall_success=0
    fi
done

if [ $overall_success == 1 ]
then
    echo "All tests sucessful.  This code is now acceptable"
    exit 0
else
    echo "At least one test unsucessful.  This code is not yet acceptable."
    exit 1
fi
