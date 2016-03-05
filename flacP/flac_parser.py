"""
The module is end-user module. Allow simple parse flac from bytearray
"""
from frames_parser import Frame
from header_parser import Header

__author__ = 'Skipper'


class Parser:
    """
    The class is end-user class - if you wanna use my code, just import
    this class
    """
    def __init__(self, file: bytearray):
        self.file = file
        self.frames_shift = 0

    def parse_header(self):
        """
        The method print all information about your flac
        :return: null
        """
        sync_code = 'xyza'
        shift = 0
        for index, byte in enumerate(self.file):
            sync_code = sync_code[-3:] + chr(byte)
            if sync_code == 'fLaC':
                shift = index-3
                break
        header = Header.get_header_from_bytes(self.file[shift+4:], shift+4)
        shift += header.length + 4
        self.frames_shift = shift
        return header

    def parse_frames(self):
        if not self.frames_shift:
            self.parse_header()
        shift = self.frames_shift
        frames = Frame.frame_from_bytes(self.file[shift:], shift)
        return frames
