#!/bin/bash

gcc -std=c99 -Wl,-wrap,main -lm primestuff.c primestuff_standard_funcs.o test_primestuff_functions.o -o test_primestuff_functions_exe

./test_primestuff_functions_exe
