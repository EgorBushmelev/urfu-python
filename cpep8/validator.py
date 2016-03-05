"""
Module for code parsing and validation
"""
__author__ = 'Skipper'
from pep_parser import Parser


class Validator:
    """
    The class for end-users. It contains sources and validate() method
    """

    def __init__(self, source):
        self.source = source
        self.messages = {}
        self.parser = Parser()

    def validate(self):
        """
        The method validate source code to PEP-0008
        :return:dict
        """
        for index, line in enumerate(self.source):
            result = self.parser.parse(line)
            if result:
                if index in self.messages.keys():
                    self.messages[index].extend(result)
                else:
                    self.messages[index] = result
        self.parser.reset()
        return self.messages
