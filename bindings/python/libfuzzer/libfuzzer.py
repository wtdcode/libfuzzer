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

# FUZZER_INTERFACE_VISIBILITY int
# LLVMFuzzerRunDriver(int *argc, char ***argv,
#                     int (*UserCb)(const uint8_t *Data, size_t Size),
#                     uint8_t *Counters, size_t CountersSize);

_libfuzzer.LLVMFuzzerRunDriver.restype = ctypes.c_int
_libfuzzer.LLVMFuzzerRunDriver.argtypes = (ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_size_t)

USERCB = ctypes.CFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_size_t)

def CreateLibFuzzerCounters(Size: int):
    return (ctypes.c_uint8 * Size)()

def LLVMFuzzerRunDriver(Argv: List[str], TestOneInputCallback: Callable[[bytes], int], Counters: ctypes.Array):
    
    def _callback_wrapper(bs, sz):
        return TestOneInputCallback(bytes((ctypes.c_char * sz).from_address(bs)))

    argc = ctypes.c_int(len(Argv))
    argv = (ctypes.c_void_p * (len(Argv) + 1))()

    for idx, arg in enumerate(Argv):
        argv[idx] = ctypes.cast(ctypes.create_string_buffer(arg.encode("utf-8")), ctypes.c_void_p)

    # ctypes.cast(argv, ctypes.c_void_p) -> char** (remember argv is an array!)
    argv = ctypes.cast(argv, ctypes.c_void_p)
    # now ctypes.cast(argv, ctypes.c_void_p) -> char*** (argv now is a pointer)
    
    return _libfuzzer.LLVMFuzzerRunDriver(
        ctypes.cast(ctypes.addressof(argc), ctypes.c_void_p), 
        ctypes.cast(ctypes.addressof(argv), ctypes.c_void_p), 
        ctypes.cast(USERCB(_callback_wrapper), ctypes.c_void_p), 
        ctypes.cast(Counters, ctypes.c_void_p), 
        len(Counters))