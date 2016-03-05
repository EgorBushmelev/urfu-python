"""
The module works with DNS. Can be used standalone.
"""
__author__ = 'Skipper'
DEFAULT_PORT = 53
DEFAULT_SERVER = '8.8.8.8'
DEFAULT_TIMEOUT = 5
DEFAULT_NUM_OF_RETRIES = 4

import socket
from debugmode import Debugger
from packet import QueryPacket, ReceivedPacket


class NoResponseException(Exception):
    """
    Exception raised when no response
    """
    pass


class Resolver:
    """
    The class works with network and parse data from packets
    """

    NAME_NOT_FOUND = [(-1,)]
    NO_RESPONSE = [(-2,)]
    TYPES = {1: 'A', 2: 'NS', 5: 'CNAME', 15: 'MX', 28: 'AAAA'}

    def __init__(self, server=DEFAULT_SERVER, debug_mode=False,
                 port=DEFAULT_PORT, num_of_retries=DEFAULT_NUM_OF_RETRIES,
                 waiting=DEFAULT_TIMEOUT):
        self.address = ''
        self.identifier = 0
        self.servers = [server]
        self.port = port
        self.num_of_retries = num_of_retries
        self.timeout = waiting
        self.visited_servers = []
        self.debugger = Debugger(debug_mode)

    def resolve(self, address):
        """
        This shit resolve everything from address.
        :param address: str
        :return: tuple
        """
        self.identifier += 1
        packet = QueryPacket(self.identifier)
        packet.add_question(address, QueryPacket.QU_A)

        try:
            received_packet = self._send_packet_(packet.get_packet(),
                                                 self.servers[0])
        except ReceivedPacket.NotFoundException:
            return self.NAME_NOT_FOUND
        except NoResponseException:
            return self.NO_RESPONSE
        #  recursion, baby!
        if len(received_packet.answers) == 0:
            self.servers = []
            self._add_servers_(received_packet)
            while (self.servers != []) and (len(received_packet.answers) == 0):
                try:
                    self.identifier += 1
                    packet.increment_id()
                    received_packet = self._send_packet_(packet.get_packet(),
                                                         self.servers[0])
                    self._add_servers_(received_packet)
                except ReceivedPacket.NotFoundException:
                    return self.NAME_NOT_FOUND
                except NoResponseException:
                    if len(self.servers) == 1:
                        return self.NO_RESPONSE
                finally:
                    if len(self.servers) > 1:
                        self.servers = self.servers[1:]
                    else:
                        self.servers = self.NAME_NOT_FOUND
        return self._format_result_(received_packet.get_answers())

    @staticmethod
    def _format_result_(answers):
        result = []
        for record in answers:
            result.append((record.record_type, record.get_data()))
        return result

    def _add_servers_(self, packet):
        for record in packet.authoritative_nameservers:
            if (record.record_type == QueryPacket.QU_A)\
                    or (record.record_type == QueryPacket.QU_NS):
                if record.get_data() not in self.visited_servers:
                    self.servers.append(record.get_data())

    def _send_packet_(self, packet, server):
        sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # udp yoba
        sender.settimeout(self.timeout)
        sender.connect((server, self.port))
        self.debugger.send_packet(server, self.identifier)
        raw_received = None
        number_of_tries = 0
        while raw_received is None and number_of_tries < self.num_of_retries:
            try:
                number_of_tries += 1
                sender.send(packet)
                raw_received = sender.recv(512)
            except socket.timeout:
                self.debugger.timeout(server)
        sender.close()
        if raw_received is None:
            self.debugger.no_response(server)
            raise NoResponseException
        received_packet = ReceivedPacket(raw_received)
        self.debugger.receive_packet(received_packet, server, self.identifier)
        return received_packet
