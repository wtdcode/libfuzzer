# libfuzzer

This is modified version of libfuzzer.

## API

```C
// Mandatory user-provided target function.
// Executes the code under test with [Data, Data+Size) as the input.
// libFuzzer will invoke this function *many* times with different inputs.
// Must return 0.
typedef int (*TestOneInputCallback)(const uint8_t *Data, size_t Size);

// Optional user-provided initialization function.
// If provided, this function will be called by libFuzzer once at startup.
// It may read and modify argc/argv.
// Must return 0.
typedef int (*InitializeCallback)(int *argc, char ***argv);

// Optional user-provided custom mutator.
// Mutates raw data in [Data, Data+Size) inplace.
// Returns the new size, which is not greater than MaxSize.
// Given the same Seed produces the same mutation.
typedef size_t (*CustomMutatorCallback)(uint8_t *Data, size_t Size,
                                        size_t MaxSize, unsigned int Seed);

// Optional user-provided custom cross-over function.
// Combines pieces of Data1 & Data2 together into Out.
// Returns the new size, which is not greater than MaxOutSize.
// Should produce the same mutation given the same Seed.
typedef size_t (*CustomCrossOverCallback)(const uint8_t *Data1, size_t Size1,
                                          const uint8_t *Data2, size_t Size2,
                                          uint8_t *Out, size_t MaxOutSize,
                                          unsigned int Seed);

// Experimental, may go away in future.
// libFuzzer-provided function to be used inside LLVMFuzzerCustomMutator.
// Mutates raw data in [Data, Data+Size) inplace.
// Returns the new size, which is not greater than MaxSize.
FUZZER_INTERFACE_VISIBILITY size_t
LLVMFuzzerMutate(uint8_t *Data, size_t Size, size_t MaxSize);

// The main entry of the fuzzer.
FUZZER_INTERFACE_VISIBILITY int
LLVMFuzzerRunDriver(int *argc, char ***argv, TestOneInputCallback UserCb,
                    InitializeCallback InitCb, CustomMutatorCallback MutCb,
                    CustomCrossOverCallback CrossCb, uint8_t *Counters,
                    size_t CountersSize);
```

With a little hack, this version of libfuzzer exposes the extra counters defined in `FuzzerExtraCounters.cpp`, which make it esay to use libfuzzer as a library.

## Example

```C
#include "LibFuzzer.h"
#include <stdio.h>

static uint8_t Counters[4096];

int Test(const uint8_t *p, size_t s) {
  // Instrument the code manually.
  if (s == 0) {
    Counters[0]++;
  } else if (s == 8) {
    Counters[1]++;
  } else if (s == 16) {
    Counters[2]++;
    abort();
  } else {
    Counters[3]++;
  }
  Counters[4]++;
  return 0;
}

int Init(int *argc, char ***argv) { printf("Initialized!\n"); }

size_t Mutate(uint8_t *Data, size_t Size, size_t MaxSize, unsigned int Seed) {
  return LLVMFuzzerMutate(Data, Size, MaxSize);
}

size_t CrossOver(const uint8_t *Data1, size_t Size1, const uint8_t *Data2,
                 size_t Size2, uint8_t *Out, size_t MaxOutSize,
                 unsigned int Seed) {
  return 0; // Do nothing
}

int main(int argc, char **argv) {
  LLVMFuzzerRunDriver(&argc, &argv, Test, Init, Mutate, CrossOver,
                      (uint8_t *)Counters, 4096);
}
```