import ctypes
from typing import Callable, List
import pkg_resources
import sys
import distutils
import distutils.sysconfig
import os

from pathlib import Path

_lib = {'darwin': 'libfuzzer.dylib',
        'linux': 'libfuzzer.so',
        'linux2': 'libfuzzer.so'}.get(sys.platform, "libfuzzer.so")

_path_list = [Path(pkg_resources.resource_filename(__name__, 'lib')),
              Path(os.path.realpath(__file__)).parent / "lib",
              Path(''),
              Path(distutils.sysconfig.get_python_lib()),
              Path("/usr/local/lib/" if sys.platform ==
                   'darwin' else '/usr/lib64'),
              Path(os.getenv('PATH', ''))]


def _load_lib(path: Path):
    try:
        return ctypes.cdll.LoadLibrary(path / _lib)
    except OSError as e:
        return None


_libfuzzer = None

for _p in _path_list:
    _libfuzzer = _load_lib(_p)
    if _libfuzzer is not None:
        break
else:
    raise ImportError("Fail to load the dynamic library for libfuzzer.")

PArgcType = ctypes.POINTER(ctypes.c_int)
PArgvType = ctypes.POINTER(ctypes.POINTER(ctypes.c_char_p))
PUint8 = ctypes.c_void_p # By design to reduce ctypes.cast

_libfuzzer.LLVMFuzzerRunDriver.restype = ctypes.c_int
_libfuzzer.LLVMFuzzerRunDriver.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)
_libfuzzer.LLVMFuzzerMutate.restype = ctypes.c_size_t
_libfuzzer.LLVMFuzzerMutate.argtypes = (ctypes.c_void_p, ctypes.c_size_t, ctypes.c_size_t)


TestOneInputCB = ctypes.CFUNCTYPE(ctypes.c_int, PUint8, ctypes.c_size_t)
InitializeCB = ctypes.CFUNCTYPE(ctypes.c_int, PArgcType, PArgvType)
CustomMutatorCB = ctypes.CFUNCTYPE(ctypes.c_size_t, PUint8, ctypes.c_size_t, ctypes.c_size_t, ctypes.c_uint)
CustomCrossOverCB = ctypes.CFUNCTYPE(ctypes.c_size_t,
    PUint8, ctypes.c_size_t,
    PUint8, ctypes.c_size_t, 
    PUint8, ctypes.c_size_t, 
    ctypes.c_uint)

def CreateLibFuzzerCounters(Size: int):
    return (ctypes.c_uint8 * Size)()

def LLVMFuzzerMutate(Data: ctypes.Array, MaxSize: int):

    return _libfuzzer.LLVMFuzzerMutate(Data, len(Data), MaxSize)

def LLVMFuzzerRunDriver(Argv: List[str],
                        TestOneInputCallback: Callable[[ctypes.Array], int], 
                        InitializeCallback: Callable[[List[ctypes.c_char_p]], int],
                        CustomMutatorCallback: Callable[[ctypes.Array, int, int], int],
                        CustomCrossOverCallback: Callable[[ctypes.Array, ctypes.Array, ctypes.Array, int], int],
                        Counters: ctypes.Array):
    
    def _test_one_input_wrapper(data: PUint8, size: int):
        return TestOneInputCallback((ctypes.c_uint8 * size).from_address(data))

    def _initialize_wrapper(pargc: PArgcType, pargv: PArgvType):
        argc = pargc.contents.value
        argv = (ctypes.c_char_p * (argc + 1)).from_address(ctypes.cast(pargv.contents, ctypes.c_void_p).value)
        return InitializeCallback(argv)
    
    def _custom_mutator_wrapper(data: PUint8, size: int, max_size: int, seed: int):
        return CustomMutatorCallback((ctypes.c_uint8 * size).from_address(data), max_size, seed)
    
    def _custom_cross_over_wrapper(
        data1: PUint8, size1: int, 
        data2: PUint8, size2: int, 
        out: PUint8, out_size: int, 
        seed: int):
        return CustomCrossOverCallback(
            (ctypes.c_uint8 * size1).from_address(data1),
            (ctypes.c_uint8 * size2).from_address(data2),
            (ctypes.c_uint8 * out_size).from_address(out),
            seed
        )

    argc = ctypes.c_int(len(Argv))
    argv = (ctypes.c_void_p * (len(Argv) + 1))()

    for idx, arg in enumerate(Argv):
        argv[idx] = ctypes.cast(ctypes.create_string_buffer(arg.encode("utf-8")), ctypes.c_void_p)

    # ctypes.cast(argv, ctypes.c_void_p) -> char** (recall argv was an array!) &(char*[]) -> char**
    argv = ctypes.cast(argv, ctypes.c_void_p)
    # ctypes.cast(argv, ctypes.c_void_p) -> char*** since argv is a pointer now &char** -> char***

    refs = (TestOneInputCB(_test_one_input_wrapper), InitializeCB(_initialize_wrapper), CustomMutatorCB(_custom_mutator_wrapper), CustomCrossOverCB(_custom_cross_over_wrapper))

    return _libfuzzer.LLVMFuzzerRunDriver(
        ctypes.cast(ctypes.addressof(argc), ctypes.c_void_p), 
        ctypes.cast(ctypes.addressof(argv), ctypes.c_void_p), 
        ctypes.cast(refs[0], ctypes.c_void_p),
        ctypes.cast(refs[1], ctypes.c_void_p),
        ctypes.cast(refs[2], ctypes.c_void_p),
        ctypes.cast(refs[3], ctypes.c_void_p),
        ctypes.cast(Counters, ctypes.c_void_p), 
        len(Counters))