"""
The module is utility. Parse binary information to objects.
"""
__author__ = 'Skipper'


class MetaBlock:
    """
    The class describe structure of metablock
    """
    def __init__(self, header, data, global_shift):
        self.block_type = header.block_type
        self.data_length = header.length
        self.last = header.last
        self.data = data
        self.global_shift = global_shift

    @staticmethod
    def get_metablock_from_bytes(raw_bytes: bytearray, global_shift):
        """
        The static method parse binary data into object
        :param raw_bytes: bytearray
        :param global_shift: int
        :return: MetaBlock
        """
        header = MetaBlockHeader.metablock_header_from_bytes(raw_bytes)
        raw_data = raw_bytes[4:4 + header.length]
        data = MetaBlockData.get_metablock_data(header.block_type, raw_data,
                                                global_shift + 4)
        return MetaBlock(header, data, global_shift)

    def get_length(self):
        """
        The method returns length of MetaBlock
        :return: int
        """
        return 4 + self.data_length

    def is_last(self):
        """
        The method return is the block last
        :return: bool
        """
        return self.last

    def print_info(self):
        """
        The method print info about block
        :return: null
        """
        print(hex(self.global_shift)[2:].zfill(8) + ': Header of block')
        print(hex(self.global_shift)[2:].zfill(8) + ': Block type is '
              + self._get_block_type())
        print(hex(self.global_shift)[2:].zfill(8) + ': Is last block - '
              + str(self.is_last()))
        print(hex(self.global_shift + 1)[2:].zfill(8) + '-'
              + hex(self.global_shift + 3)[2:].zfill(8) + ': Data size is '
              + str(self.data_length))
        print(hex(self.global_shift + 4)[2:].zfill(8) + ': Block data')
        self.data.print_info()

    def _get_block_type(self):
        block_type = {0: 'STREAMINFO',
                      1: 'PADDING',
                      2: 'APPLICATION',
                      3: 'SEEKTABLE',
                      4: 'VORBIS_COMMENT',
                      5: 'CUESHEET',
                      6: 'PICTURE'}
        if self.block_type in block_type.keys():
            return block_type[self.block_type]
        else:
            return 'UNKNOWN'


class MetaBlockHeader:
    """
    The class describes structure of block header
    """
    def __init__(self, last: bool, block_type, length):
        self.last = last
        self.block_type = block_type
        self.length = length

    @staticmethod
    def metablock_header_from_bytes(raw_bytes: bytearray):
        """
        The method parse binary data into object
        :param raw_bytes: bytearray
        :return: MetaBlockHeader
        """
        last = False if (raw_bytes[0] >> 7) == 0 else True
        block_type = raw_bytes[0] % 128
        length = (raw_bytes[1] << 16) + (raw_bytes[2] << 8) + raw_bytes[3]
        return MetaBlockHeader(last, block_type, length)


class MetaBlockData:
    """
    The class is abstract for typed data classes
    """
    def __init__(self, global_shift, raw_data=bytearray()):
        self.global_shift = global_shift

    def print_info(self):
        """
        Print data info
        :return: null
        """
        pass

    def _print_w(self, line, shift, size):
        if size == 1:
            print(hex(shift + self.global_shift)[2:].zfill(8) + ': ' + line)
        else:
            print(hex(shift + self.global_shift)[2:].zfill(8)
                  + '-' + hex(shift + self.global_shift + size)[2:].zfill(8)
                  + ': ' + line)

    @staticmethod
    def get_metablock_data(block_type, raw_bytes: bytearray, global_shift):
        """
        The method parse binary data into object
        :param block_type: int
        :param raw_bytes: bytearray
        :param global_shift: int
        :return: MetaBlockData
        """
        result = {}
        function_dict = {0: MetaBlockDataStreamInfo,
                         1: MetaBlockDataPadding,
                         2: MetaBlockData,
                         3: MetaBlockDataSeekTable,
                         4: MetaBlockDataVorbisComments,
                         5: MetaBlockDataCuesheet,
                         6: MetaBlockDataPicture}
        if block_type in function_dict.keys():
            result = function_dict[block_type](global_shift, raw_bytes)
        return result


class MetaBlockDataStreamInfo(MetaBlockData):
    """
    Data class for STREAMINFO
    """
    def __init__(self, global_shift, raw_bytes: bytearray):
        super().__init__(global_shift)
        self.min_block_size = (raw_bytes[0] << 8) + raw_bytes[1], 0, 2
        self.max_block_size = (raw_bytes[2] << 8) + raw_bytes[3], 2, 2
        self.min_frame_size = ((raw_bytes[4] << 16) + (raw_bytes[5] << 8)
                               + raw_bytes[6]), 4, 3
        self.max_frame_size = ((raw_bytes[7] << 16) + (raw_bytes[8] << 8)
                               + raw_bytes[9]), 7, 3
        self.sample_rate = ((raw_bytes[10] << 12) + (raw_bytes[11] << 4)
                            + (raw_bytes[12] >> 4)), 10, 3
        self.number_of_channels = (raw_bytes[12] % 16) >> 1, 12, 1
        self.bits_per_sample = (((raw_bytes[12] % 2) << 4)
                                + (raw_bytes[13] >> 4)), 12, 2
        self.total_samples_in_stream = ((raw_bytes[13] % 16) << 20
                                        + (raw_bytes[14] << 16)
                                        + (raw_bytes[15] << 8)
                                        + (raw_bytes[16])), 13, 4
        if self.total_samples_in_stream[0] == 0:
            self.total_samples_in_stream = 'Unknown', 13, 4
        self.md5_checksum = raw_bytes[17:33], 17, 16

    def print_info(self):
        """
        Description is the same as in the parent class
        :return: null
        """
        self._print_w('Minimal block size is ' + str(self.min_block_size[0]),
                      self.min_block_size[1], self.min_block_size[2])
        self._print_w('Maximal block size is ' + str(self.max_block_size[0]),
                      self.max_block_size[1], self.max_block_size[2])
        self._print_w('Minimal frame size is ' + str(self.min_frame_size[0]),
                      self.min_frame_size[1], self.min_frame_size[2])
        self._print_w('Maximal frame size is ' + str(self.max_frame_size[0]),
                      self.max_frame_size[1], self.max_frame_size[2])
        self._print_w('Sample rate is ' + str(self.sample_rate[0]),
                      self.sample_rate[1], self.sample_rate[2])
        self._print_w('Number of channels is '
                      + str(self.number_of_channels[0]),
                      self.number_of_channels[1], self.number_of_channels[2])
        self._print_w('Bits per sample: ' + str(self.bits_per_sample[0]),
                      self.bits_per_sample[1], self.bits_per_sample[2])
        self._print_w('Total samples in stream: '
                      + str(self.max_frame_size[0]),
                      self.max_frame_size[1], self.max_frame_size[2])
        self._print_w('MD5 checksum: ' + str(self.md5_checksum[0]),
                      self.md5_checksum[1], self.md5_checksum[2])


class MetaBlockDataPadding(MetaBlockData):
    """
    Data class for PADDING
    """
    def __init__(self, global_shift, raw_bytes: bytearray):
        super().__init__(global_shift)
        self.padding_size = len(raw_bytes)

    def print_info(self):
        """
        Description is the same as in the parent class
        :return: null
        """
        print(hex(self.global_shift)[2:].zfill(8) + '-'
              + hex(self.global_shift + self.padding_size)[2:].zfill(8)
              + ': Padding size is ' + str(self.padding_size))


class MetaBlockDataSeekTable(MetaBlockData):
    """
    Data class for SEEKTABLE
    """
    def __init__(self, global_shift, raw_bytes: bytearray):
        super().__init__(global_shift)
        self.seek_points = []
        shift = 0
        while shift < len(raw_bytes):
            sample_number = 0
            for i in range(8):
                sample_number = (sample_number << 8) + raw_bytes[shift + i]
            sample_number = sample_number, shift, 8
            offset = 0
            for i in range(8, 16):
                offset = (offset << 8) + raw_bytes[shift + i]
            offset = offset, shift + 8, 8
            numbers_of_samples = ((raw_bytes[shift + 16] << 8)
                                  + raw_bytes[shift + 17]), shift + 16, 2
            seek_point = {'sample_number': sample_number,
                          'offset': offset,
                          'num_of_samples': numbers_of_samples}
            self.seek_points.append(seek_point)
            shift += 18

    def print_info(self):
        """
        Description is the same as in the parent class
        :return: null
        """
        for point in self.seek_points:
            self._print_w('Sample number :' + str(point['sample_number'][0]),
                          point['sample_number'][1], point['sample_number'][2])
            self._print_w('Point offset :' + str(point['offset'][0]),
                          point['offset'][1], point['offset'][2])
            self._print_w('Number of samples :'
                          + str(point['num_of_samples'][0]),
                          point['num_of_samples'][1],
                          point['num_of_samples'][2])


class MetaBlockDataVorbisComments(MetaBlockData):
    """
    Data class for VorbisComments
    """
    def __init__(self, global_shift, raw_bytes: bytearray):
        super().__init__(global_shift)
        self.vendor_name_length = (raw_bytes[0] + (raw_bytes[1] << 8)
                                   + (raw_bytes[2] << 16)
                                   + (raw_bytes[3] << 24), 0, 4)
        self.vendor = (
            raw_bytes[4:4 + self.vendor_name_length[0]].decode('utf-8'),
            4, self.vendor_name_length[0])
        shift = 4 + self.vendor_name_length[0]
        self.fields_number = (raw_bytes[shift] + (raw_bytes[shift + 1] << 8)
                              + (raw_bytes[shift + 2] << 16)
                              + (raw_bytes[shift + 3] << 24), shift, 4)
        shift += 4
        self.comments = []
        for i in range(self.fields_number[0]):
            length = (raw_bytes[shift]
                      + (raw_bytes[shift + 1] << 8)
                      + (raw_bytes[shift + 2] << 16)
                      + (raw_bytes[shift + 3] << 24))
            shift += 4
            comment = (raw_bytes[shift:shift + length].decode('utf-8'),
                       shift, length)
            shift += length
            self.comments.append(comment)

    def print_info(self):
        """
        Description is the same as in the parent class
        :return:
        """
        self._print_w('Length of vendor name is '
                      + str(self.vendor_name_length[0]),
                      self.vendor_name_length[1], self.vendor_name_length[2])
        self._print_w('Vendor is ' + str(self.vendor[0]), self.vendor[1],
                      self.vendor[2])
        for comment in self.comments:
            self._print_w('Comment: ' + comment[0], comment[1], comment[2])


class MetaBlockDataCuesheet(MetaBlockData):
    """
    Data class for CUESHEET
    """
    def __init__(self, global_shift, raw_bytes: bytearray):
        super().__init__(global_shift)
        self.catalog_number = ''
        counter = 0
        for byte in raw_bytes:
            if counter > 127:
                break
            if byte != 0:
                self.catalog_number += chr(byte)
                counter += 1
            else:
                break
        self.catalog_number = self.catalog_number, 0, 128
        shift = 128
        self.leadin_samples_num = 0
        for i in range(8):
            self.leadin_samples_num = ((self.leadin_samples_num << 8)
                                       + raw_bytes[shift + i])
        self.leadin_samples_num = self.leadin_samples_num, 128, 8
        shift += 8
        self.is_cd = True if raw_bytes[shift] > 0 else False, shift, 1
        shift += 259
        self.num_of_tracks = raw_bytes[shift], shift, 1
        shift += 1
        self.tracks = []
        for i in range(self.num_of_tracks[0]):
            offset = 0
            for j in range(8):
                offset = (offset << 8) + raw_bytes[shift + j]
            offset = offset, shift, 8
            shift += 8
            track_number = raw_bytes[shift], shift, 1
            shift += 1
            isrc = ''
            for j in range(12):
                isrc += chr(raw_bytes[shift + j])
            isrc = isrc, shift, 12
            shift += 12
            is_audio = (True if (raw_bytes[shift] // 128) == 0 else False,
                        shift, 1)
            is_pre_emphasis = (True if ((raw_bytes[shift] % 128) // 64) == 1
                               else False, shift, 1)
            shift += 14
            num_of_track_index_points = raw_bytes[shift], shift, 1
            shift += 1
            track_indexes = []
            for j in range(num_of_track_index_points[0]):
                index_offset = 0
                for k in range(8):
                    index_offset = (index_offset << 8) + raw_bytes[shift]
                index_offset = index_offset, shift, 8
                shift += 8
                index_number = raw_bytes[shift], shift, 1
                track_indexes.append({'index_offset': index_offset,
                                      'index_number': index_number})
                shift += 4
            self.tracks.append({'track_offset': offset,
                                'track_number': track_number,
                                'isrc': isrc,
                                'track_type': is_audio,
                                'pre_emphasis': is_pre_emphasis,
                                'track_index_points': track_indexes})

    def print_info(self):
        """
        Description is the same as in the parent class
        :return:
        """
        self._print_w('Catalog number is ' + str(self.catalog_number[0]),
                      self.catalog_number[1], self.catalog_number[2])
        self._print_w('Number of lead-in samples'
                      + str(self.leadin_samples_num[0]),
                      self.leadin_samples_num[1], self.leadin_samples_num[2])
        self._print_w('Is CD: ' + str(self.is_cd[0]), self.is_cd[1],
                      self.is_cd[2])
        self._print_w('Number of tracks: ' + str(self.num_of_tracks[0]),
                      self.num_of_tracks[1], self.num_of_tracks[2])
        for track in self.tracks:
            self._print_w('Track offset: ' + str(track['track_offset'][0]),
                          track['track_offset'][1], track['track_offset'][2])
            self._print_w('Track number: ' + str(track['track_number'][0]),
                          track['track_number'][1], track['track_number'][2])
            self._print_w('ISRC: ' + track['isrc'][0],
                          track['isrc'][1], track['isrc'][2])
            self._print_w('Track type: ' + str(track['track_type'][0]),
                          track['track_type'][1], track['track_type'][2])
            self._print_w('Is pre emphasis: ' + str(track['pre_emphasis'][0]),
                          track['pre_emphasis'][1], track['pre_emphasis'][2])
            for point in track['track_index_points']:
                self._print_w('Index point offset: '
                              + str(point['index_offset'][0]),
                              point['index_offset'][1],
                              point['index_offset'][2])
                self._print_w('Index point number: '
                              + str(point['index_number'][0]),
                              point['index_number'][1],
                              point['index_number'][2])


class MetaBlockDataPicture(MetaBlockData):
    """
    Data class for PICTURE
    """
    def __init__(self, global_shift, raw_bytes: bytearray):
        super().__init__(global_shift)
        self.picture_type = ((raw_bytes[0] << 24)
                             + (raw_bytes[1] << 16)
                             + (raw_bytes[2] << 8)
                             + raw_bytes[3], 0, 4)
        self.mime_length = ((raw_bytes[4] << 24)
                            + (raw_bytes[5] << 16)
                            + (raw_bytes[6] << 8)
                            + raw_bytes[7], 4, 4)
        shift = 8
        self.mime_type = ''
        for i in range(self.mime_length[0]):
            self.mime_type += chr(raw_bytes[shift + i])
        self.mime_type = self.mime_type, shift, self.mime_length[0]
        shift += self.mime_length[0]
        self.description_length = ((raw_bytes[shift] << 24)
                                   + (raw_bytes[shift + 1] << 16)
                                   + (raw_bytes[shift + 2] << 8)
                                   + raw_bytes[shift + 3], shift, 4)
        shift += 4
        self.description = (
            raw_bytes[shift:shift
                      + self.description_length[0]].decode('utf-8'),
            shift, self.description_length[0])
        shift += self.description_length[0]
        self.width = ((raw_bytes[shift] << 24)
                      + (raw_bytes[shift + 1] << 16)
                      + (raw_bytes[shift + 2] << 8)
                      + raw_bytes[shift + 3], shift, 4)
        shift += 4
        self.height = ((raw_bytes[shift] << 24)
                       + (raw_bytes[shift + 1] << 16)
                       + (raw_bytes[shift + 2] << 8)
                       + raw_bytes[shift + 3], shift, 4)
        shift += 4
        self.color_depth = ((raw_bytes[shift] << 24)
                            + (raw_bytes[shift + 1] << 16)
                            + (raw_bytes[shift + 2] << 8)
                            + raw_bytes[shift + 3], shift, 4)
        shift += 4
        self.used_colors_num = ((raw_bytes[shift] << 24)
                                + (raw_bytes[shift + 1] << 16)
                                + (raw_bytes[shift + 2] << 8)
                                + raw_bytes[shift + 3], shift, 4)
        shift += 4
        self.picture_size = ((raw_bytes[shift] << 24)
                             + (raw_bytes[shift + 1] << 16)
                             + (raw_bytes[shift + 2] << 8)
                             + raw_bytes[shift + 3], shift, 4)
        shift += 4
        self.picture_data = (raw_bytes[shift:shift + self.picture_size[0]],
                             shift, self.picture_size[0])

    def print_info(self):
        """
        Description is the same as in the parent class
        :return:
        """
        self._print_w('Picture type: ' + str(self.picture_type[0]),
                      self.picture_type[1], self.picture_type[2])
        self._print_w('MIME length: ' + str(self.mime_length[0]),
                      self.mime_length[1], self.mime_length[2])
        self._print_w('MIME type: ' + str(self.mime_type[0]),
                      self.mime_type[1], self.mime_type[2])
        self._print_w('Picture description length: '
                      + str(self.description_length[0]),
                      self.description_length[1], self.description_length[2])
        self._print_w('Picture description: ' + str(self.description[0]),
                      self.description[1], self.description[2])
        self._print_w('Picture width: ' + str(self.width[0]),
                      self.width[1], self.width[2])
        self._print_w('Picture height: ' + str(self.height[0]),
                      self.height[1], self.height[2])
        self._print_w('Color depth: ' + str(self.color_depth[0]),
                      self.color_depth[1], self.color_depth[2])
        self._print_w('Used colors: ' + str(self.used_colors_num[0]),
                      self.used_colors_num[1], self.used_colors_num[2])
        self._print_w('Picture size: ' + str(self.picture_size[0]),
                      self.picture_size[1], self.picture_size[2])
        self._print_w('Picture data is located here', self.picture_data[1],
                      self.picture_data[2])
