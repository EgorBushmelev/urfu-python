"""
The module should parse frames
"""
__author__ = 'Skipper'


class Frame:
    """
    The class describes frame structure
    """

    def __init__(self, blocking_strategy, block_size, sample_rate, length,
                 channel_assignment, sample_size, number, global_shift, crc,
                 frame_number):
        self.blocking_strategy = blocking_strategy
        self.block_size = block_size
        self.sample_rate = sample_rate
        self.length = length
        self.channel_assignment = channel_assignment
        self.sample_size = sample_size
        self.number = number
        self.global_shift = global_shift
        self.crc16 = crc
        self.frame_number = frame_number

    def print_info(self):
        """
        The method prints all info about frame
        :return: null
        """
        def _heex(num):
            return hex(num)[2:].zfill(8)

        print(_heex(self.global_shift) + ':Frame #' + str(self.frame_number))
        print(_heex(self.blocking_strategy[1])
              + ':Blocking strategy of frame is '
              + ('variable' if self.blocking_strategy[0] else 'fixed'))
        print(_heex(self.block_size[1])
              + ':Size of blocks is ' + str(self.block_size[0]))
        print(_heex(self.sample_rate[1])
              + ':Sample rate of this frame is '
              + str(self.sample_rate[0])
              + ' Hz')
        print(_heex(self.channel_assignment[1])
              + ':Channels assignment is '
              + self.channel_assignment[0]
              + ' channels')
        print(_heex(self.sample_size[1])
              + ':Sample size is '
              + self.sample_size[0])
        if self.blocking_strategy:
            print(_heex(self.number[1])
                  + ':Sample number in frame is '
                  + str(self.number[0]))
        else:
            print(_heex(self.number[1])
                  + ':Frame number in frame is '
                  + str(self.number[0]))
        print(_heex(self.crc16[1])
              + ':CRC checksum is ' + str(self.crc16[0]))
        data_start = self.crc16[1] + 1
        data_end = self.global_shift + self.length - 1
        print(_heex(data_start) + '-' + _heex(data_end)
              + ':Frame data')

    @staticmethod
    def frame_from_bytes(raw_bytes: bytearray, global_shift):
        """
        The method parse bytes into list of frames
        :param raw_bytes: bytearray
        :param global_shift: int
        :return: list
        """
        def _my_pow(num, degree):
            result = 1
            if degree:
                for _ in range(degree):
                    result = result * num
            return result

        shift = 0
        block_sizes = {0: 'reserved',
                       1: '192 samples',
                       2: '576 * (2^(n-2)) samples',
                       3: '576 * (2^(n-2)) samples',
                       4: '576 * (2^(n-2)) samples',
                       5: '576 * (2^(n-2)) samples',
                       8: '256 * (2^(n-8)) samples',
                       9: '256 * (2^(n-8)) samples',
                       10: '256 * (2^(n-8)) samples',
                       11: '256 * (2^(n-8)) samples',
                       12: '256 * (2^(n-8)) samples',
                       13: '256 * (2^(n-8)) samples',
                       14: '256 * (2^(n-8)) samples',
                       15: '256 * (2^(n-8)) samples'}
        sample_rates = {0: 'Like as in STREAMINFO',
                        1: '88200',
                        2: '176400',
                        3: '192000',
                        4: '8000',
                        5: '16000',
                        6: '22050',
                        7: '24000',
                        8: '32000',
                        9: '44100',
                        10: '48000',
                        11: '96000',
                        15: 'invalid'}
        channels = {8: 'left/side stereo 2',
                    9: 'right/side stereo 2',
                    10: 'mid/side stereo 2',
                    11: 'reserved',
                    12: 'reserved',
                    13: 'reserved',
                    14: 'reserved',
                    15: 'reserved'}
        sample_sizes = {0: 'Like as in STREAMINFO',
                        1: '8 bits per sample',
                        2: '12 bits per sample',
                        3: 'reserved',
                        4: '16 bits per sample',
                        5: '20 bits per sample',
                        6: '24 bits per sample',
                        7: 'reserved'}
        frames_shift_list = []
        frames = []
        while True:
            if (shift + 2) == len(raw_bytes):
                frames_shift_list.append(shift + 2)
                break
            if ((raw_bytes[shift] == 255)
                    and ((raw_bytes[shift + 1] >> 2) == 62)):
                frames_shift_list.append(shift)
                shift += 2
            else:
                shift += 1
        for index, local_shift in enumerate(frames_shift_list[:-1]):
            shift = local_shift
            blocking_strategy = (raw_bytes[shift + 1],
                                 global_shift + shift + 1, 1)
            shift += 2
            block_size = raw_bytes[shift] >> 4, global_shift + shift, 1
            sample_rate = raw_bytes[shift] % 16, global_shift + shift, 1
            shift += 1
            channel_assignment = raw_bytes[shift] >> 4, global_shift + shift, 1
            if channel_assignment[0] > 8:
                channel_assignment = (channels[channel_assignment[0]],
                                      channel_assignment[1],
                                      channel_assignment[2])
            else:
                channel_assignment = (str(channel_assignment[0]),
                                      channel_assignment[1],
                                      channel_assignment[2])
            sample_size = (sample_sizes[(raw_bytes[shift] % 16) >> 1],
                           global_shift + shift, 1)
            shift += 1
            if raw_bytes[shift] < 128:
                number = raw_bytes[shift], global_shift + shift, 1
                shift += 1
            else:
                raw_number_length = raw_bytes[shift]
                number_length = (int(raw_number_length > 223)
                                 + int(raw_number_length > 239)
                                 + int(raw_number_length > 247)
                                 + int(raw_number_length > 251)
                                 + 2)
                number = raw_number_length % _my_pow(2, 8 - number_length)
                for i in range(number_length - 1):
                    number = (number << 6) + (raw_bytes[shift + 1 + i] % 64)
                number = number, global_shift + shift, number_length
                shift += number_length
            if 5 < block_size[0] < 8:
                if block_size[0] % 2:
                    block_size = (
                        (raw_bytes[shift] << 8) + raw_bytes[shift + 1],
                        block_size[1], block_size[2])
                    shift += 2
                else:
                    block_size = raw_bytes[shift], block_size[1], block_size[2]
                    shift += 1
            else:
                block_size = (block_sizes[block_size[0]],
                              block_size[1], block_size[2])
            if 11 < sample_rate[0] < 15:
                if sample_rate[0] % 12:
                    rate = (((raw_bytes[shift] << 8) + raw_bytes[shift + 1])
                            * _my_pow(10, (sample_rate[0] % 4) - 1))
                    sample_rate = (str(rate), sample_rate[1], sample_size[2])
                    shift += 2
                else:
                    sample_rate = (str(raw_bytes[shift]), sample_rate[1],
                                   sample_size[2])
                    shift += 1
            else:
                sample_rate = (sample_rates[sample_rate[0]],
                               sample_rate[1], sample_rate[2])
            crc_8 = raw_bytes[shift], global_shift + shift, 1
            length = frames_shift_list[index + 1] - frames_shift_list[index]
            frames.append(Frame(blocking_strategy, block_size, sample_rate,
                                length, channel_assignment, sample_size,
                                number, local_shift + global_shift,
                                crc_8, index))
        return frames
