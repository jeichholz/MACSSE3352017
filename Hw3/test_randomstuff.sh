#!/bin/bash

gcc -std=c99 -Wl,-wrap,main -lm randomstuff.c randomstuff_standard.o test_randomstuff.o -o test_randomstuff_exe

./test_randomstuff_exe
