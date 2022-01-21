# libfuzzer

This is modified version of libfuzzer.

## API

```C
FUZZER_INTERFACE_VISIBILITY int
LLVMFuzzerRunDriver(int *argc, char ***argv,
                    int (*UserCb)(const uint8_t *Data, size_t Size),
                    uint8_t *Counters, size_t CountersSize);
```

With a little hack, this version of libfuzzer exposes the extra counters in `LLVMFuzzerRunDriver`, which make it esay to use libfuzzer as a librray.

## Example

```C
#include "LibFuzzer.h"

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

int main(int argc, char** argv) {
    LLVMFuzzerRunDriver(&argc, &argv, Test, (uint8_t *)Counters, 4096);
}
```