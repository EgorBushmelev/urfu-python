"""
The module add some debugging features
"""
__author__ = 'Skipper'


class Debugger:
    """
    The class add some debugging features
    """
    def __init__(self, activated):
        self.activated = activated

    @staticmethod
    def _log_(text, identifier=-1):
        if identifier < 0:
            print('\t\t{}'.format(text))
        else:
            print('{:<4} {}'.format(identifier, text))

    @staticmethod
    def _log_rr_(shift, name, packet_type, data):
        types = {1: 'A', 2: 'NS', 5: 'CNAME', 15: 'MX', 28: 'AAAA'}
        if packet_type in types:
            text = '{}:\t{}\t{}\t{}'.format('{:0>4}'.format(hex(shift)[2:]),
                                            name, types[packet_type], data)
            print('\t\t{}'.format(text))

    def send_packet(self, server, identifier):
        """
        The method logs the sending of packet
        :param server: str
        :param identifier: int
        :return: None
        """
        if self.activated:
            if identifier > 1:
                self._log_('Recursive iteration #{}'.format(identifier-1))
            self._log_('Recursion-desired A query sent to {}'.format(server),
                       identifier)

    def receive_packet(self, packet, server, identifier):
        """
        The method logs the receiving of packet
        :param packet: ReceivedPacket
        :param server: str
        :param identifier: id
        :return: None
        """
        if self.activated:
            self._log_('Response received from {}'.format(server), identifier)
            self._print_hexdump_(packet)
            self._log_('Server is {}authoritative'.format(
                '' if packet.aa else 'not '))
            self._log_('Recursion is {}available'.format(
                '' if packet.ra else 'not '))
            self._log_('Reply code: {}'.format(
                'No error' if packet.rcode == 0 else 'Name not found'))
            self._log_('Answer RRS: {}'.format(packet.answer_quantity))
            self._log_('Authority RRS: {}'.format(packet.authority_quantity))
            if packet.answer_quantity > 0:
                self._log_('Answers:')
                for record in packet.answers:
                    self._log_rr_(record.global_shift, record.name,
                                  record.record_type, record.data)
            else:
                self._log_('Name not found here')
            if packet.authority_quantity > 0:
                self._log_('Authoritative nameservers:')
                for record in packet.authoritative_nameservers:
                    self._log_rr_(record.global_shift, record.name,
                                  record.record_type, record.data)

    def timeout(self, server):
        """
        The method logs the timeout of request
        :param server: str
        :return: None
        """
        if self.activated:
            self._log_('Server {}, time limit exceed'.format(server))

    def no_response(self, server):
        """
        The method logs that no response
        :param server: str
        :return: None
        """
        if self.activated:
            self._log_('The server {} does not response'.format(server))
            self._log_('Try to connect to another server')

    def _print_hexdump_(self, packet):
        self._log_('Hexdump:')
        block_size_counter = 0
        blocks_in_line_counter = 0
        string = '\t'
        for byte in packet.raw_packet:
            if (blocks_in_line_counter == 4) and (block_size_counter == 4):
                self._log_(string)
                string = '\t'
                block_size_counter = 0
                blocks_in_line_counter = 0

            if block_size_counter == 4:
                string += ' '
                blocks_in_line_counter += 1
                block_size_counter = 0
            string += '{:0>2}'.format(hex(byte)[2:])
            block_size_counter += 1
