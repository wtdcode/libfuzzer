#!/usr/bin/env python3

from libfuzzer import *
import os
import sys

Counters = CreateLibFuzzerCounters(4096)

def TestOneInput(input):
    # Instrument the code manually.
    l = len(input)

    if l == 0:
        Counters[0] += 1
    elif l == 8:
        Counters[1] += 1
    elif l == 16:
        Counters[2] += 1
        os.abort()
    else:
        Counters[3] += 1
    
    Counters[4] += 1
    return 0

def Initialize(argv):
    return 0

def Mutator(data, max_size, seed):
    return LLVMFuzzerMutate(data, max_size)

def CrossOver(data1, data2, out, seed):
    return 0

# If you are using -fork=1, make sure run it like `python3 ./example.py` or
# `./example.py` instead of `python3 example.py`.
LLVMFuzzerRunDriver(sys.argv, TestOneInput, Initialize, Mutator, CrossOver, Counters)
