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