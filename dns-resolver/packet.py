"""
The module works with DNS-protocol's packets: can make and parse it.
"""
__author__ = 'Skipper'

import copy


class Query:
    """
    Class for queries in QueryPacket and ReceivedPacket.
    Can form bytearray query.
    """

    def __init__(self, address, query_type, query_class=1):
        self.query_name = address
        self.query_class = query_class
        self.query_type = query_type

    def form_question(self):
        """
        This method form question packet
        :return: bytearray
        """
        question = ''
        question.encode('utf8')
        parts = self.query_name.split('.')
        for part in parts:
            question += chr(len(bytearray(part, 'utf8')))
            question += part
        bquestion = bytearray(question, 'utf8')
        bquestion.extend((0, 0, self.query_type, 0, self.query_class))
        return bquestion

    @staticmethod
    def query_from_bytes(answer: bytearray):
        """
        The method initialize Query-object from raw packet
        :param answer: bytearray
        :return: Query
        """
        pointer = 0
        query_name = ''  # одинаковый код - исправить
        while answer[pointer] != 0:
            for j in range(answer[pointer]):
                query_name += chr(answer[pointer+j+1])
            query_name += '.'
            pointer += answer[pointer] + 1
        pointer += 1
        query_type = (answer[pointer] << 8) + answer[pointer+1]
        query_class = (answer[pointer+2] << 8) + answer[pointer+3]
        return Query(query_name, query_type, query_class), pointer+4


class ResourceRecord:
    """
    Class for resource records in ReceivedPacket.
    May be initialized from bytearray and can parse data.
    """

    def __init__(self, global_shift, name, record_type,
                 query_class, ttl, length, data: bytearray, packet):
        self.global_shift = global_shift
        self.name = name
        self.record_type = record_type
        self.query_class = query_class
        self.ttl = ttl
        self.length = length
        self.raw_data = data
        self.packet = packet
        self.data = self._decode_data_()

    @staticmethod
    def resource_record_from_bytes(global_shift, name,
                                   raw_record: bytearray, packet):
        """
        The method initialize ResourceRecord-object from raw packet
        :param global_shift: int
        :param name: str
        :param raw_record: bytearray
        :param packet: ReceivedPacket
        :return: ResourceRecord
        """
        record_type = (raw_record[0] << 8) + raw_record[1]
        query_class = (raw_record[2] << 8) + raw_record[3]
        ttl = (raw_record[4] << 24) + (raw_record[5] << 16)\
            + (raw_record[6] << 8) + raw_record[7]
        length = (raw_record[8] << 8) + raw_record[9]
        data = raw_record[10:(10+length)]
        record = ResourceRecord(global_shift, name, record_type,
                                query_class, ttl, length, data, packet)
        return record, 10+length

    def _decode_data_(self):
        switch = {QueryPacket.QU_A: self._decode_a_,
                  QueryPacket.QU_AAAA: self._decode_aaaa_,
                  QueryPacket.QU_CNAME: self._decode_cname_,
                  QueryPacket.QU_NS: self._decode_ns_,
                  QueryPacket.QU_MX: self._decode_mx_}
        if self.record_type in switch:
            return switch[self.record_type]()
        else:
            return ''

    def _decode_a_(self):
        data = ".".join(map(str, self.raw_data[0:4]))
        return data

    def _decode_cname_(self):
        data = self.packet.get_string(self.raw_data, 0)[0]
        return data

    def _decode_mx_(self):
        preference = self.raw_data[0] << 8 + self.raw_data[1]
        mail_exchange = self.packet.get_string(self.raw_data, 2)[0]
        return preference, mail_exchange

    def _decode_aaaa_(self):
        ipv6_address = ''
        hex_data = []
        for block in self.raw_data:
            hex_data.append('{:0>2}'.format(str(hex(block))[2:]))
        for index, block in enumerate(hex_data):
            ipv6_address += block
            if (index % 2) == 1:
                ipv6_address += ':'
        return ipv6_address[:-1]

    def _decode_ns_(self):
        data = self.packet.get_string(self.raw_data, 0)[0]
        return data

    def get_data(self):
        """
        Getter for data-field
        :return:str
        """
        return self.data


class QueryPacket:
    """
    The class form request sent to server.
    """

    OP_DIRECT = 0  # прямой запрос
    OP_INVERSE = 1  # инверсный запрос
    OP_STATUS = 2  # запрос статуса сервера
    RE_DISABLED = 0  # рекурсия НИНУЖНА
    RE_ENABLED = 1
    QU_A = 1  # A query
    QU_NS = 2  # NS query
    QU_CNAME = 5  # canonical name query
    QU_PTR = 12  # pointer record
    QU_HINFO = 13  # host information
    QU_MX = 15  # MX query
    QU_AAAA = 28  # A query
    QU_AXFR = 252  # запрос на передачу зоны
    QU_ANY = 255  # запрос всех записей

    def __init__(self, identifier, opcode=OP_DIRECT, recursion=RE_ENABLED):
        self.identifier = identifier
        self.qr = 0  # 0 - запрос, 1 - ответ
        self.opcode = opcode
        # 0 - прямой, 1 - инверсный, 2 - запрос статуса сервера
        self.aa = 0  # только для ответа
        self.tc = 0  # только для ответа
        self.rd = recursion  # требуется рекурсия 0/1
        self.ra = 0  # только для ответа
        self.rcode = 0  # только для ответа
        self.questions = []

    def add_question(self, address, query_type, query_class=1):
        """
        The method add new question to QueryPacket
        :param address: str
        :param query_type: int
        :param query_class: int
        :return: None
        """
        # query_class равен 1 для интернета.
        # остальное нинужна
        self.questions.append(Query(address, query_type, query_class))

    def _form_header_(self):
        header = bytearray()
        # id
        header.extend([self.identifier // 256, self.identifier % 256])
        # flags
        flag = self.qr
        flag <<= 4
        flag += self.opcode
        flag <<= 2
        flag += self.rd
        header.extend([flag, 0, len(self.questions) // 256,
                       len(self.questions) % 256, 0, 0, 0, 0, 0, 0])
        return header

    def _form_questions_(self):
        if len(self.questions) == 0:
            raise Exception('there is no questions')
        questions = bytearray()
        for question in self.questions:
            questions.extend(question.form_question())
        return questions

    def get_packet(self):
        """
        The method return complete packet for request
        :return: bytearray
        """
        packet = bytearray()
        packet.extend(self._form_header_())
        packet.extend(self._form_questions_())
        return packet

    def increment_id(self):
        """
        The method increment identifier in QueryPacket
        :return: None
        """
        self.identifier += 1


class ReceivedPacket:
    """
    The class parse packet received from server
    """

    class NotFoundException(Exception):
        """
        Exception raised when name not found
        """
        pass

    def __init__(self, received: bytearray):
        self.raw_packet = copy.deepcopy(received)
        if len(received) < 12:
            raise Exception('To small packet')
        self.identifier = (received[0] << 8) + received[1]
        self.qr = received[2] // 128  # 0 - запрос, 1 - ответ
        if self.qr != 1:
            raise Exception('It is query packet')
        self.opcode = (received[2] % 128) // 8
        # 0 - прямой, 1 - инверсный, 2 - запрос статуса сервера
        self.aa = (received[2] % 8) // 4  # только для ответа
        self.tc = (received[2] % 4) // 2  # только для ответа
        self.rd = received[2] % 2  # требуется рекурсия 0/1
        self.ra = received[3] // 128  # только для ответа
        self.rcode = received[3] % 16  # только для ответа
        if self.rcode == 3:
            raise self.NotFoundException
        self.query_quantity = (received[4] << 8) + received[5]
        self.answer_quantity = (received[6] << 8) + received[7]
        self.authority_quantity = (received[8] << 8) + received[9]
        self.additional_info_quantity = (received[10] << 8) + received[11]
        self.answers = []
        self.queries = []
        self.authoritative_nameservers = []
        self._parse_answers_()
        pass

    def _parse_answers_(self):
        pointer = 12
        for i in range(self.query_quantity):
            query, length = Query.query_from_bytes(self.raw_packet[pointer:])
            pointer += length
            self.queries.append(query)
        for i in range(self.answer_quantity + self.authority_quantity):
            rr_start_pointer = pointer
            name, real_length = self.get_string(self.raw_packet, pointer)
            pointer += real_length
            record, record_length = ResourceRecord.resource_record_from_bytes(
                rr_start_pointer, name, self.raw_packet[pointer:], self)
            if i < self.answer_quantity:
                self.answers.append(record)
            else:
                self.authoritative_nameservers.append(record)
            pointer += record_length

    def get_string(self, data: bytearray, position):
        """
        The method find string by pointer in DNS-type strings
        :param data: bytearray
        :param position: int
        :return: str
        """
        pointer = position
        string = ''
        real_length = 0
        while data[pointer] != 0:
            if (data[pointer] >> 6) == 3:
                real_length = pointer - position + 2
                string += self.get_string(self.raw_packet,
                                          ((data[pointer] - 192) << 8)
                                          + data[pointer+1])[0]
                break
            for i in range(data[pointer]):
                string += chr(data[pointer+i+1])
            string += '.'
            pointer += data[pointer] + 1
            real_length += 1
        if string[-1:] == '.':
            string = string[:-1]
        return string, real_length

    def get_answers(self):
        """
        The method return list of received ResourceRecords
        :return: list
        """
        return self.answers

    def is_authority(self):
        """
        The method tell the server is authority or not
        :return: int
        """
        return self.aa
