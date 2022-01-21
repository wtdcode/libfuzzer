cmake_minimum_required(VERSION 3.10)

project(libfuzzer)

set(PROJECT_IS_TOP_LEVEL OFF)
if(CMAKE_CURRENT_SOURCE_DIR STREQUAL CMAKE_SOURCE_DIR)
    set(PROJECT_IS_TOP_LEVEL ON)
    
    # Enable folder support
    set_property(GLOBAL PROPERTY USE_FOLDERS ON)
endif()

option(BUILD_SHARED_LIBS "Build shared instead of static library" ${PROJECT_IS_TOP_LEVEL})

set(LIBFUZZER_SOURCES
  llvm/compiler-rt/lib/fuzzer/FuzzerCrossOver.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerDataFlowTrace.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerDriver.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerExtFunctionsDlsym.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerExtFunctionsWeak.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerExtFunctionsWindows.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerExtraCounters.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerFork.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerIO.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerIOPosix.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerIOWindows.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerLoop.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerMerge.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerMutate.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerSHA1.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerTracePC.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerUtil.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerUtilDarwin.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerUtilFuchsia.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerUtilLinux.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerUtilPosix.cpp
  llvm/compiler-rt/lib/fuzzer/FuzzerUtilWindows.cpp)

set (CMAKE_CXX_STANDARD 11)

if (UNIX)
set(LIBFUZZER_CFLAGS "-fno-omit-frame-pointer")
endif()

add_library(fuzzer ${LIBFUZZER_SOURCES})

target_include_directories(fuzzer PUBLIC include/)
target_include_directories(fuzzer PRIVATE llvm/compiler-rt/lib/fuzzer/)
target_compile_options(fuzzer PRIVATE ${LIBFUZZER_CFLAGS})

if (UNIX)
target_link_libraries(fuzzer PRIVATE pthread)
endif()

add_executable(example example/main.c)
target_link_libraries(example fuzzer)