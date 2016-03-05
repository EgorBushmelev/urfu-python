flac parser
Author: Egor Bushmelev, CS-201

usage: flacp.py [-h] [-a] [-g] N
example: tone24bit.flac

This program required GStreamer 1.0 and gst-plugins installed. The easiest way to use GStreamer 1.0 is to download the latest version from: http://sourceforge.net/projects/pygobjectwin32/files/

positional arguments:
  N           flac file name

optional arguments:
  -h, --help  show this help message and exit
  -a, --all   print all info about file
  -g, --gen   print general information about file