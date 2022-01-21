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
    LLVMFuzzerRunDriver(&argc, &argv, Test, (char*)Counters, 4096);
}