import setuptools
import sys
import os
import subprocess
import shutil
import platform
from distutils.util import get_platform
from distutils.command.build import build as _build
from distutils.command.sdist import sdist as _sdist
from setuptools.command.bdist_egg import bdist_egg as _bdist_egg
from setuptools.command.develop import develop as _develop
from distutils.command.clean import clean as _clean
from pathlib import Path

SYSTEM = sys.platform

# sys.maxint is 2**31 - 1 on both 32 and 64 bit mingw
IS_64BITS = platform.architecture()[0] == '64bit'

# are we building from the repository or from a source distribution?
ROOT_DIR = Path(os.path.realpath(__file__)).parent
LIBS_DIR = ROOT_DIR / 'libfuzzer' / 'lib'
HEADERS_DIR = ROOT_DIR / 'libfuzzer' / 'include'
SRC_DIR = ROOT_DIR / '..' / '..'
BUILD_DIR = SRC_DIR / 'build_python'

VERSION = "0.0.2"

if SYSTEM == 'darwin':
    LIBRARY_FILE = "libfuzzer.dylib"
    STATIC_LIBRARY_FILE = None
else:
    LIBRARY_FILE = "libfuzzer.so"
    STATIC_LIBRARY_FILE = None

def clean_builds():
    shutil.rmtree(LIBS_DIR, ignore_errors=True)
    shutil.rmtree(HEADERS_DIR, ignore_errors=True)

def build_libfuzzer():
    prev_cwd = os.getcwd()
    clean_builds()
    os.mkdir(LIBS_DIR)
    #os.mkdir(HEADERS_DIR)

    shutil.copytree(SRC_DIR / "include" , HEADERS_DIR) 
    
    os.chdir(SRC_DIR)

    if not os.path.exists(BUILD_DIR):
        os.mkdir(BUILD_DIR)
    
    if os.getenv("DEBUG", ""):
        args = ["cmake", "-B", BUILD_DIR, "-DCMAKE_BUILD_TYPE=Debug"]
    else:
        args = ["cmake", "-B", BUILD_DIR, "-DCMAKE_BUILD_TYPE=Release"]

    subprocess.check_call(args)

    os.chdir(BUILD_DIR)
    threads = os.getenv("THREADS", "6")
    subprocess.check_call(["make", "-j" + threads])

    shutil.copy(LIBRARY_FILE, LIBS_DIR)

    os.chdir(prev_cwd)


class build(_build):
    def run(self):
        build_libfuzzer()
        return _build.run(self)

class clean(_clean):
    def run(self):
        clean_builds()
        return _clean.run(self)

class develop(_develop):
    def run(self):
        build_libfuzzer()
        return _develop.run(self)

class bdist_egg(_bdist_egg):
    def run(self):
        self.run_command('build')
        return _bdist_egg.run(self)

# https://stackoverflow.com/questions/45150304/how-to-force-a-python-wheel-to-be-platform-specific-when-building-it
# https://github.com/unicorn-engine/unicorn/blob/198e432a1d7edbed6f4726acc42c50c3a4141b6b/bindings/python/setup.py#L229
if 'bdist_wheel' in sys.argv and '--plat-name' not in sys.argv:
    idx = sys.argv.index('bdist_wheel') + 1
    sys.argv.insert(idx, '--plat-name')
    name = get_platform()
    if 'linux' in name:
        # linux_* platform tags are disallowed because the python ecosystem is fubar
        # linux builds should be built in the centos 5 vm for maximum compatibility
        # see https://github.com/pypa/manylinux
        # see also https://github.com/angr/angr-dev/blob/master/bdist.sh
        sys.argv.insert(idx + 1, 'manylinux1_' + platform.machine())
    elif 'mingw' in name:
        if IS_64BITS:
            sys.argv.insert(idx + 1, 'win_amd64')
        else:
            sys.argv.insert(idx + 1, 'win32')
    else:
        # https://www.python.org/dev/peps/pep-0425/
        sys.argv.insert(idx + 1, name.replace('.', '_').replace('-', '_'))

long_desc = '''
libfuzzer
-----------

This is raw bindings for libfuzzer which works as a library.

Example:

```python
#!/usr/bin/env python3

from libfuzzer import *
import os
import sys

Counters = CreateLibFuzzerCounters(4096)

def TestOneInput(input):
    # Instrument the code manually.
    l = len(input)

    if l == 0:
        Counters[0] += 1
    elif l == 8:
        Counters[1] += 1
    elif l == 16:
        Counters[2] += 1
        os.abort()
    else:
        Counters[3] += 1
    
    Counters[4] += 1
    return 0

def Initialize(argv):
    return 0

def Mutator(data, max_size, seed):
    return LLVMFuzzerMutate(data, max_size)

def CrossOver(data1, data2, out, seed):
    return 0

# If you are using -fork=1, make sure run it like `python3 ./example.py` or
# `./example.py` instead of `python3 example.py`.
LLVMFuzzerRunDriver(sys.argv, TestOneInput, Initialize, Mutator, CrossOver, Counters)
```

'''

setuptools.setup(
    provides=['libfuzzer'],
    packages=['libfuzzer'],
    name='libfuzzer',
    version=VERSION,
    author='Lazymio',
    author_email='mio@lazym.io',
    description='Raw bindings for a modified version of libfuzzer.',
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url='https://github.com/wtdcode/libfuzzer',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    requires=['ctypes'],
    cmdclass={
        "build" : build,
        "develop" : develop,
        "bdist_egg" : bdist_egg,
        "clean" : clean
    },
    zip_safe=False,
    include_package_data=True,
    is_pure=False,
    package_data={
        'libfuzzer': ['lib/*', 'include/*']
    }
)
