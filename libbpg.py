'''
 * BPG decoder
 *
 * The C version Copyright (c) 2014 Fabrice Bellard
 * The Python version is "translated" and copyrighted by Lee June, 2014
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 * THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 * THE SOFTWARE.
 */
 '''

__version__='0.9.4'
__date__='Dec 27, 2014'

from enum import Enum

from ctypes import *

DLL=CDLL('bpg.dll')

class BPGDecoderContext(Structure):
    pass

class BPGImageFormatEnum(Enum):
    (
    BPG_FORMAT_GRAY,
    BPG_FORMAT_420, #/* chroma at offset (0.5, 0.5) (JPEG) */
    BPG_FORMAT_422, #/* chroma at offset (0.5, 0) (JPEG) */
    BPG_FORMAT_444,
    BPG_FORMAT_420_VIDEO, #/* chroma at offset (0, 0.5) (MPEG2) */
    BPG_FORMAT_422_VIDEO, #/* chroma at offset (0, 0) (MPEG2) */
    )=range(6)



class BPGColorSpaceEnum(Enum):
    (
    BPG_CS_YCbCr,
    BPG_CS_RGB,
    BPG_CS_YCgCo,
    BPG_CS_YCbCr_BT709,
    BPG_CS_YCbCr_BT2020,

    BPG_CS_COUNT,
    )=range(6)


class BPGImageInfo(Structure):
    _fields_ = [
        ("width", c_int),
        ("height", c_int),
        ("format", c_int), #/* see BPGImageFormatEnum */
        ("has_alpha", c_int), #/* TRUE if an alpha plane is present */
        ("color_space", c_int), #/* see BPGColorSpaceEnum */
        ("bit_depth", c_int),
        ("premultiplied_alpha", c_int), #/* TRUE if the color is alpha premultiplied */
        ("has_w_plane", c_int), #/* TRUE if a W plane is present (for CMYK encoding) */
        ("limited_range", c_int), #/* TRUE if limited range for the color */
    ]


class BPGExtensionTagEnum(Enum):
    BPG_EXTENSION_TAG_EXIF = 1
    BPG_EXTENSION_TAG_ICCP = 2
    BPG_EXTENSION_TAG_XMP = 3
    BPG_EXTENSION_TAG_THUMBNAIL = 4

#since there is pointer to BPGExtensionData itself,
#we have to define class like this, then add _fields_ later
class BPGExtensionData(Structure):
    pass

BPGExtensionData._fields_ = [
        ("tag", c_uint8), #any way to use BPGExtensionTagEnum?
        ("buf_len", c_uint32),
        ("buf", POINTER(c_uint8)),
        ("next", POINTER(BPGExtensionData))
    ]

class BPGDecoderOutputFormat(Enum):
    (
    BPG_OUTPUT_FORMAT_RGB24,
    BPG_OUTPUT_FORMAT_RGBA32, #/* not premultiplied alpha */
    BPG_OUTPUT_FORMAT_RGB48,
    BPG_OUTPUT_FORMAT_RGBA64, #/* not premultiplied alpha */
    )=range(4)

BPG_DECODER_INFO_BUF_SIZE = 16

######################################
#                                                define the functions                                                               #
######################################
_bpg_decoder_open=DLL.bpg_decoder_open
_bpg_decoder_open.argtypes=None
_bpg_decoder_open.restype=POINTER(BPGDecoderContext)
def bpg_decoder_open():
    '''
    BPGDecoderContext *bpg_decoder_open(void);
    '''
    return _bpg_decoder_open()


_bpg_decoder_keep_extension_data=DLL.bpg_decoder_keep_extension_data
_bpg_decoder_keep_extension_data.argtypes=[POINTER(BPGDecoderContext), c_int]
_bpg_decoder_keep_extension_data.restype=None
def bpg_decoder_keep_extension_data(s, enable):
    '''
    void bpg_decoder_keep_extension_data(BPGDecoderContext *s, int enable);

    If enable is true, extension data are kept during the image
    decoding and can be accessed after bpg_decoder_decode() with
    bpg_decoder_get_extension(). By default, the extension data are
    discarded. *
    '''
    _bpg_decoder_keep_extension_data(s, enable);


_bpg_decoder_decode=DLL.bpg_decoder_decode
_bpg_decoder_decode.argtypes=[POINTER(BPGDecoderContext), POINTER(c_uint8), c_int]
_bpg_decoder_decode.restype=c_int
def bpg_decoder_decode(s, buf, buf_len):
    '''
    int bpg_decoder_decode(BPGDecoderContext *s, const uint8_t *buf, int buf_len);

    return 0 if 0K, < 0 if error
    '''

    #print 'type(s)=',type(s)
    #print  'type(buf)=',type(buf)
    #print 'required types=', _bpg_decoder_decode.argtypes

    buf=cast(buf, POINTER(c_uint8))
    return _bpg_decoder_decode(s, buf, buf_len);


_bpg_decoder_get_extension_data=DLL.bpg_decoder_get_extension_data
_bpg_decoder_get_extension_data.argtypes=[POINTER(BPGDecoderContext)];
_bpg_decoder_get_extension_data.restype=POINTER(BPGDecoderContext);
def bpg_decoder_get_extension_data(s):
    '''
    BPGExtensionData *bpg_decoder_get_extension_data(BPGDecoderContext *s);

    Return the first element of the extension data list
    '''
    return _bpg_decoder_get_extension_data(s);


_bpg_decoder_get_info=DLL.bpg_decoder_get_info
_bpg_decoder_get_info.argtypes=[POINTER(BPGDecoderContext), POINTER(BPGImageInfo)]
_bpg_decoder_get_info.restype=c_int
def bpg_decoder_get_info(s, p):
    '''
    int bpg_decoder_get_info(BPGDecoderContext *s, BPGImageInfo *p);

    return 0 if 0K, < 0 if error
    '''
    #print _bpg_decoder_get_info.argtypes
    #print type(s)
    #print type(p)
    #p=p.contents

    return _bpg_decoder_get_info(s, p)


_bpg_decoder_start=DLL.bpg_decoder_start
_bpg_decoder_start.argtypes=[POINTER(BPGDecoderContext), c_int] #any way to use BPGDecoderOutputFormat]
_bpg_decoder_start.restype=c_int
def bpg_decoder_start(s, out_fmt):
    '''
    int bpg_decoder_start(BPGDecoderContext *s, BPGDecoderOutputFormat out_fmt);

    return 0 if 0K, < 0 if error
    '''
    return _bpg_decoder_start(s, out_fmt)


_bpg_decoder_get_line=DLL.bpg_decoder_get_line
_bpg_decoder_get_line.argtypes=[POINTER(BPGDecoderContext), c_void_p];
_bpg_decoder_get_line.restype=c_int
def bpg_decoder_get_line(s, buf):
    '''
    int bpg_decoder_get_line(BPGDecoderContext *s, void *buf);

    return 0 if 0K, < 0 if error
    '''
    #print
    #print 'type(s)=', type(s)
    #print 'type(buf)=',type(buf)
    #print 'required types=', _bpg_decoder_get_line.argtypes
    buf=cast(buf, c_void_p)
    return _bpg_decoder_get_line(s, buf);


_bpg_decoder_close=DLL.bpg_decoder_close
_bpg_decoder_close.argtypes=[POINTER(BPGDecoderContext)];
_bpg_decoder_close.restype=None
def bpg_decoder_close(s):
    '''
    void bpg_decoder_close(BPGDecoderContext *s);
    '''
    _bpg_decoder_close(s)


_bpg_decoder_get_data=DLL.bpg_decoder_get_data
_bpg_decoder_get_data.argtypes=[POINTER(BPGDecoderContext), POINTER(c_int), c_int];
_bpg_decoder_get_data.restype=POINTER(c_uint8)
def bpg_decoder_get_data(s, pline_size, plane):
    '''
    uint8_t *bpg_decoder_get_data(BPGDecoderContext *s, int *pline_size, int plane);

    only useful for low level access to the image data
    '''
    return _bpg_decoder_get_data(s, pline_size, plane)


_bpg_decoder_get_info_from_buf=DLL.bpg_decoder_get_info_from_buf
_bpg_decoder_get_info_from_buf.argtypes=[POINTER(BPGImageInfo),
                                  POINTER(POINTER(BPGExtensionData)),
                                  POINTER(c_uint8), c_int]
_bpg_decoder_get_info_from_buf.restype=c_int
def bpg_decoder_get_info_from_buf(p,
                                  pfirst_md,
                                  buf, buf_len
                                  ):
    '''
    int bpg_decoder_get_info_from_buf(BPGImageInfo *p,
                                      BPGExtensionData **pfirst_md,
                                      const uint8_t *buf, int buf_len);

    Get information from the start of the image data in 'buf' (at least
    min(BPG_DECODER_INFO_BUF_SIZE, file_size) bytes must be given).

    If pfirst_md != NULL, the extension data are also parsed and the
    first element of the list is returned in *pfirst_md. The list must
    be freed with bpg_decoder_free_extension_data().

    Return 0 if OK, < 0 if unrecognized data.
    '''
    return _bpg_decoder_get_info_from_buf(p,
                                  pfirst_md,
                                  buf, buf_len
                                  );


_bpg_decoder_free_extension_data=DLL.bpg_decoder_free_extension_data
_bpg_decoder_free_extension_data.argtypes=[POINTER(BPGExtensionData)]
_bpg_decoder_free_extension_data.restype=None
def bpg_decoder_free_extension_data(first_md):
    '''
    void bpg_decoder_free_extension_data(BPGExtensionData *first_md);

    Free the extension data returned by bpg_decoder_get_info_from_buf()
    '''
    _bpg_decoder_free_extension_data(first_md)

