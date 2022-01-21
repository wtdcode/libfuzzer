//===- FuzzerExtraCounters.cpp - Extra coverage counters ------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//
// Extra coverage counters defined by user code.
//===----------------------------------------------------------------------===//

#include "FuzzerPlatform.h"
#include <cstdint>

namespace fuzzer {

static uint8_t *CountersBegin;
static uint8_t *CountersEnd;

void SetExtraCounters(uint8_t *Begin, uint8_t *End) {
  CountersBegin = Begin;
  CountersEnd = End;
}

uint8_t *ExtraCountersBegin() { return CountersBegin; }
uint8_t *ExtraCountersEnd() { return CountersEnd; }
ATTRIBUTE_NO_SANITIZE_ALL
void ClearExtraCounters() {  // hand-written memset, don't asan-ify.
  uintptr_t *Beg = reinterpret_cast<uintptr_t*>(ExtraCountersBegin());
  uintptr_t *End = reinterpret_cast<uintptr_t*>(ExtraCountersEnd());
  for (; Beg < End; Beg++) {
    *Beg = 0;
    __asm__ __volatile__("" : : : "memory");
  }
}

}  // namespace fuzzer
