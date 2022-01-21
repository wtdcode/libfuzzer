#ifndef LIB_FUZZER_H
#define LIB_FUZZER_H

#include <stdint.h>
#include <stdlib.h>

#if defined(_WIN32)
#define FUZZER_INTERFACE_VISIBILITY __declspec(dllexport)
#else
#define FUZZER_INTERFACE_VISIBILITY __attribute__((visibility("default")))
#endif

#ifdef __cplusplus
extern "C" {
#endif // __cplusplus

FUZZER_INTERFACE_VISIBILITY int
LLVMFuzzerRunDriver(int *argc, char ***argv,
                    int (*UserCb)(const uint8_t *Data, size_t Size),
                    uint8_t *Counters, size_t CountersSize);

#ifdef __cplusplus
} // extern "C"
#endif // __cplusplus

#endif