#ifndef LIB_FUZZER_H
#define LIB_FUZZER_H

#include <stdint.h>
#include <stdlib.h>

#ifndef FUZZER_INTERFACE_VISIBILITY
#if defined(_WIN32)
#define FUZZER_INTERFACE_VISIBILITY __declspec(dllexport)
#else
#define FUZZER_INTERFACE_VISIBILITY __attribute__((visibility("default")))
#endif
#endif

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

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

#ifdef __cplusplus
} // extern "C"
#endif // __cplusplus

#endif