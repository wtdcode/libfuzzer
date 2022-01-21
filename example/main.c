#include "LibFuzzer.h"

static uint8_t Counters[4096];

int Test(const uint8_t *p, size_t s) {
    if (s == 16) {
        abort();
    }
    Counters[s]++;
    return 0;
}

int main(int argc, char** argv) {
    LLVMFuzzerRunDriver(&argc, &argv, Test, (char*)Counters, 4096);
}