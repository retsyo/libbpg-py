
                    Copyright (c) 2014 Lee June

=1. What

This is a pure python binding via CTYPES for BPG (Better Portable Graphics,
http://bellard.org/bpg/, Fabrice Bellard)  Image format.

=2. Where

https://github.com/retsyo/BPG_python

=3. How

1) You should compile libbpg into dynamic library. To do so, a minor modified
Makefile ( the original one is in libbpg-0.9.4.tar.gz from http://bellard.org/bpg/)
is supplied here.

2) libbpg.py covers all in libbpg.h, which is the base of the python binding.
bpgdec.py can only decode a BPG file into PPM, and there is no PNG output currently;
however bpgdec.c can write both PPM and PNG.
There is no bpgenc.py till now.


=4. Bugs or future plans

1) I only use Windows, and this binding uses 32-bit bpg.dll, which is compiled
with MINGW. I don't know whether all python source files runs ok on Linux with
your fresh dynamic library.

2) Maybe there needs more 'cast' in some functions in libbpg.py.

3) Maybe later, a PIL/Pillow plugin for I/O BPG

=5. Bug in BPG?

D:\tmp\libbpg-0.9.4\py>..\bpgenc.exe -o test.bpg -lossless test.png
D:\tmp\libbpg-0.9.4\py>..\bpgdec.exe -o test_c_bpgdec.ppm test.bpg
D:\tmp\libbpg-0.9.4\py>e:\msys\bin\diff.exe --binary test_c_bpgdec.ppm test_py_bpgdec.ppm
However, the original test.bpg and the decoded ppm has different looks. The ppm file has some
red color in it.
Is this a BPG bug, or I misunderstood '-lossless' parameter?

=6. Licensing

BSD license