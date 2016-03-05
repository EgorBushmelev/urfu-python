"""
The module parse header of flac-file
"""
__author__ = 'Skipper'
from blocks_classes import MetaBlock


class Header:
    """
    The class describe header of flac-file
    """
    def __init__(self, metablocks, length):
        self.blocks = metablocks
        self.length = length

    def print_stream_info(self):
        """
        The method prints general info about stream
        :return: null
        """
        self.blocks[0].print_info()

    def get_blocks_num(self):
        """
        The method returns number of blocks
        :return: int
        """
        return len(self.blocks)

    @staticmethod
    def get_header_from_bytes(raw_bytes: bytearray, global_shift):
        """
        Static method, that return header
        :param raw_bytes: bytearray
        :param global_shift: int
        :return: Header
        """
        blocks = []
        shift = 0
        while True:
            block = MetaBlock.get_metablock_from_bytes(raw_bytes[shift:],
                                                       global_shift+shift)
            blocks.append(block)
            shift += block.get_length()
            if block.is_last():
                break
        return Header(blocks, shift)
