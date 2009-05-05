Python 2.3.3 (#1, Apr  6 2004, 01:47:39) 
[GCC 3.3.3 (SuSE Linux)] on linux2
Type "copyright", "credits" or "license()" for more information.

    ****************************************************************
    Personal firewall software may warn about the connection IDLE
    makes to its subprocess using this computer's internal loopback
    interface.  This connection is not visible on any external
    interface and no data is sent to or received from the Internet.
    ****************************************************************
    
IDLE 1.0.2      
>>> import PIL
>>> dir (PIL)
['__builtins__', '__doc__', '__file__', '__name__', '__path__']
>>> PIL.__doc__
>>> pring PIL.__doc__
SyntaxError: invalid syntax
>>> print PIL.__doc__
None
>>> dir(PIL.image)

Traceback (most recent call last):
  File "<pyshell#5>", line 1, in -toplevel-
    dir(PIL.image)
AttributeError: 'module' object has no attribute 'image'
>>> dir(PIL.Image)

Traceback (most recent call last):
  File "<pyshell#6>", line 1, in -toplevel-
    dir(PIL.Image)
AttributeError: 'module' object has no attribute 'Image'
>>> PIL.Image

Traceback (most recent call last):
  File "<pyshell#7>", line 1, in -toplevel-
    PIL.Image
AttributeError: 'module' object has no attribute 'Image'
>>> PIL
<module 'PIL' from '/usr/lib/python2.3/site-packages/PIL/__init__.pyc'>
>>> import _imaging
>>> import Image
>>> dir(Image)
['ADAPTIVE', 'AFFINE', 'ANTIALIAS', 'BICUBIC', 'BILINEAR', 'CONTAINER', 'CUBIC', 'DEBUG', 'EXTENSION', 'EXTENT', 'FLIP_LEFT_RIGHT', 'FLIP_TOP_BOTTOM', 'FLOYDSTEINBERG', 'FixTk', 'ID', 'Image', 'ImagePalette', 'IntType', 'LINEAR', 'MESH', 'MIME', 'MODES', 'NEAREST', 'NONE', 'NORMAL', 'OPEN', 'ORDERED', 'PERSPECTIVE', 'QUAD', 'RASTERIZE', 'ROTATE_180', 'ROTATE_270', 'ROTATE_90', 'SAVE', 'SEQUENCE', 'StringType', 'TupleType', 'UnicodeStringType', 'VERSION', 'WEB', '_E', '_ImageCrop', '_MAPMODES', '_MODEINFO', '__builtins__', '__doc__', '__file__', '__name__', '_getdecoder', '_getencoder', '_getscaleoffset', '_imaging_not_installed', '_initialized', '_showxv', '_wedge', 'blend', 'composite', 'core', 'eval', 'frombuffer', 'fromstring', 'getmodebands', 'getmodebase', 'getmodetype', 'init', 'isDirectory', 'isImageType', 'isNumberType', 'isSequenceType', 'isStringType', 'isTupleType', 'merge', 'new', 'open', 'os', 'preinit', 'register_extension', 'register_mime', 'register_open', 'register_save', 'string', 'sys']
>>> im=Image.open('lena.ppm')

Traceback (most recent call last):
  File "<pyshell#12>", line 1, in -toplevel-
    im=Image.open('lena.ppm')
  File "/usr/lib/python2.3/site-packages/PIL/Image.py", line 1543, in open
    fp = __builtin__.open(fp, "rb")
IOError: [Errno 2] No such file or directory: 'lena.ppm'
>>> im=Image.open('/usr/share/doc/packages/python-imaging/Images/lena.ppm')
>>> print im.format, im.size, im.mode
PPM (128, 128) RGB
>>> im.show()
>>> h=im.histogram()
>>> h
[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 3, 4, 1, 1, 2, 4, 10, 10, 7, 7, 13, 12, 18, 31, 31, 26, 45, 43, 50, 55, 53, 60, 84, 85, 93, 93, 68, 84, 90, 109, 93, 96, 99, 102, 118, 80, 106, 75, 71, 80, 88, 72, 80, 53, 69, 45, 54, 47, 45, 31, 38, 37, 54, 45, 33, 41, 28, 23, 31, 37, 36, 38, 40, 34, 37, 40, 50, 40, 40, 34, 31, 57, 39, 42, 48, 32, 45, 43, 49, 53, 53, 38, 50, 74, 61, 54, 48, 66, 63, 46, 47, 48, 56, 51, 53, 59, 71, 56, 61, 63, 50, 56, 67, 61, 71, 64, 68, 69, 96, 86, 107, 107, 109, 130, 119, 106, 93, 90, 93, 93, 79, 90, 89, 76, 99, 97, 110, 103, 105, 120, 113, 98, 122, 107, 104, 122, 147, 160, 134, 159, 155, 177, 203, 210, 222, 213, 205, 184, 214, 154, 176, 168, 174, 171, 197, 183, 199, 224, 254, 257, 228, 285, 226, 210, 169, 167, 159, 142, 150, 112, 144, 135, 147, 143, 154, 140, 124, 124, 88, 72, 59, 41, 43, 43, 35, 27, 19, 21, 16, 18, 12, 3, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 3, 6, 5, 10, 14, 15, 20, 24, 27, 54, 62, 66, 75, 82, 87, 94, 105, 149, 133, 131, 130, 126, 116, 125, 114, 97, 112, 96, 99, 78, 80, 73, 73, 64, 68, 65, 43, 53, 42, 50, 43, 45, 57, 48, 44, 50, 51, 53, 47, 54, 68, 61, 76, 59, 64, 63, 51, 59, 59, 58, 67, 83, 68, 77, 88, 80, 92, 107, 120, 107, 112, 115, 114, 112, 138, 106, 101, 99, 105, 100, 85, 80, 87, 105, 87, 90, 82, 89, 84, 96, 99, 85, 99, 108, 128, 123, 129, 141, 129, 151, 130, 189, 135, 158, 147, 134, 113, 112, 122, 119, 138, 117, 138, 140, 139, 169, 157, 140, 152, 146, 156, 152, 137, 130, 151, 163, 177, 178, 170, 171, 141, 135, 106, 109, 94, 102, 83, 93, 79, 80, 74, 98, 72, 77, 62, 87, 71, 84, 70, 77, 66, 60, 60, 51, 36, 41, 43, 36, 44, 44, 36, 33, 43, 49, 55, 73, 44, 50, 74, 56, 48, 57, 65, 43, 60, 55, 54, 54, 63, 64, 67, 68, 63, 59, 59, 55, 42, 21, 23, 25, 32, 14, 14, 13, 13, 10, 10, 5, 5, 3, 3, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 1, 3, 3, 8, 8, 12, 18, 28, 43, 55, 65, 71, 107, 119, 136, 145, 144, 173, 174, 192, 193, 169, 198, 164, 180, 180, 208, 181, 184, 188, 198, 211, 185, 193, 184, 211, 185, 207, 198, 174, 170, 172, 202, 180, 190, 178, 207, 193, 169, 180, 181, 192, 187, 174, 166, 149, 147, 159, 163, 159, 177, 157, 166, 159, 158, 178, 162, 162, 148, 162, 144, 164, 209, 194, 208, 193, 203, 195, 163, 173, 162, 172, 116, 132, 118, 119, 111, 102, 84, 84, 70, 54, 64, 53, 68, 56, 56, 43, 53, 45, 70, 58, 41, 43, 49, 37, 62, 64, 64, 55, 46, 45, 59, 43, 61, 53, 58, 55, 52, 51, 54, 55, 48, 47, 55, 47, 43, 41, 47, 44, 45, 40, 38, 41, 39, 45, 31, 31, 52, 45, 32, 39, 35, 27, 21, 23, 31, 23, 28, 16, 4, 10, 7, 10, 12, 10, 3, 4, 10, 7, 4, 4, 3, 0, 3, 1, 1, 5, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
>>> len(h)
768
>>> types(h)

Traceback (most recent call last):
  File "<pyshell#19>", line 1, in -toplevel-
    types(h)
NameError: name 'types' is not defined
>>> type(h)
<type 'list'>
>>> im.getpixel((10,10))
(232, 159, 100)
>>> im.getpixel((10,11))
(228, 159, 102)
>>> im.getpixel(10,11)

Traceback (most recent call last):
  File "<pyshell#23>", line 1, in -toplevel-
    im.getpixel(10,11)
TypeError: getpixel() takes exactly 2 arguments (3 given)
>>> im=Image.open('/home/andreas/ebooks/makeThem/Java-PT.3/result/Java-PT-303.bmp')
>>> print im.format, im.size, im.mode
BMP (976, 1414) 1
>>> h=im.histogram()
>>> h
[74431, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1305633]
>>> len(h)
256
>>> for x in range (976):
	for y in range(1414):
		s
