cmake_minimum_required(VERSION 3.10)

project(libfuzzer)

set(LIBFUZZER_SOURCES
  compiler-rt/lib/fuzzer/FuzzerCrossOver.cpp
  compiler-rt/lib/fuzzer/FuzzerDataFlowTrace.cpp
  compiler-rt/lib/fuzzer/FuzzerDriver.cpp
  compiler-rt/lib/fuzzer/FuzzerExtFunctionsDlsym.cpp
  compiler-rt/lib/fuzzer/FuzzerExtFunctionsWeak.cpp
  compiler-rt/lib/fuzzer/FuzzerExtFunctionsWindows.cpp
  compiler-rt/lib/fuzzer/FuzzerExtraCounters.cpp
  compiler-rt/lib/fuzzer/FuzzerFork.cpp
  compiler-rt/lib/fuzzer/FuzzerIO.cpp
  compiler-rt/lib/fuzzer/FuzzerIOPosix.cpp
  compiler-rt/lib/fuzzer/FuzzerIOWindows.cpp
  compiler-rt/lib/fuzzer/FuzzerLoop.cpp
  compiler-rt/lib/fuzzer/FuzzerMerge.cpp
  compiler-rt/lib/fuzzer/FuzzerMutate.cpp
  compiler-rt/lib/fuzzer/FuzzerSHA1.cpp
  compiler-rt/lib/fuzzer/FuzzerTracePC.cpp
  compiler-rt/lib/fuzzer/FuzzerUtil.cpp
  compiler-rt/lib/fuzzer/FuzzerUtilDarwin.cpp
  compiler-rt/lib/fuzzer/FuzzerUtilFuchsia.cpp
  compiler-rt/lib/fuzzer/FuzzerUtilLinux.cpp
  compiler-rt/lib/fuzzer/FuzzerUtilPosix.cpp
  compiler-rt/lib/fuzzer/FuzzerUtilWindows.cpp)

set (CMAKE_CXX_STANDARD 11)

if (LINUX)
set(LIBFUZZER_CFLAGS "-fno-omit-frame-pointer")
endif()

# Enable shared memory for extra counters
set(LIBFUZZER_CFLAGS "-DLIBFUZZER_SHAREDMEM")

add_library(fuzzer SHARED ${LIBFUZZER_SOURCES})

target_include_directories(fuzzer PUBLIC include/)
target_include_directories(fuzzer PRIVATE compiler-rt/lib/fuzzer/)
target_compile_options(fuzzer PRIVATE ${LIBFUZZER_CFLAGS})

add_executable(example example/main.c)
target_link_libraries(example fuzzer)