"""
The module describes abstract class "Parser" and his children,
that have parse() method.
"""
from enum import Enum

__author__ = 'Skipper'
import re


class ErrorsEnum(Enum):
    """
    Errors' enum
    """
    E101 = 'E101 indentation contains mixed spaces and tabs'
    E111 = 'E111 indentation is not a multiple of four'
    E112 = 'E112 expected an indented block'
    E113 = 'E113 unexpected indentation'
    W191 = 'W191 indentation contains tabs'
    E201 = 'E201 whitespace after ‘(‘'
    E202 = 'E202 whitespace before ‘)’'
    E203 = 'E203 whitespace before ‘:’'
    E211 = 'E211 whitespace before ‘(‘'
    E231 = 'E231 missing whitespace after ‘,’'
    E251 = 'E251 unexpected spaces around keyword / parameter equals'
    E261 = 'E261 at least two spaces before inline comment'
    E262 = 'E262 inline comment should start with ‘# ‘'
    E265 = 'E265 block comment should start with ‘# ‘'
    E266 = 'E266 too many leading ‘#’ for block comment'
    E301 = 'E301 expected 1 blank line'
    E302 = 'E302 expected 2 blank lines'
    E303 = 'E303 too many blank lines'
    E304 = 'E304 blank lines found after function decorator'
    E401 = 'E401 multiple imports on one line'
    E501 = 'E501 line too long (must be <80 characters)'
    E502 = 'E502 the backslash is redundant between brackets'


class AbstractParser:
    """
    The class is abstract class for parsers.
    If you want to add new parser, it should inherits from this class
    """

    def __init__(self):
        self.in_comment = False
        self.counter = 0

    def parse(self, line):
        """
        The method should parse line to find PEP-0008 errors
        :param line: str
        :return: list
        """
        pass

    def _check_if_docstrings(self, line):
        """
        The method check line if it's docstring
        :param line:
        :return:
        """

        pattern = re.compile(r'^\s*"""\s*$')
        if pattern.match(line) and not self.counter:
            if self.in_comment:
                self.in_comment = not self.in_comment
                return not self.in_comment
        self.counter += 1
        self.counter %= 5
        return self.in_comment


class Parser:
    """
    The class aggregate all parsers and parse line by every parser it has
    """

    def __init__(self):
        self.parsers = []
        self._generate_parsers()

    def _generate_parsers(self):
        """
        The method is parsers' fabric
        :return:
        """
        self.parsers.extend([IndentationsParser(),
                             WhitespacesParser(),
                             BlankLinesParser(),
                             ImportsParser(),
                             LineLengthParser()])

    def reset(self):
        self.parsers[0].reset()

    def parse(self, line):
        """
        The method made full check of line
        :param line: str
        :return: list
        """
        messages = []
        for parser in self.parsers:
            result = parser.parse(line)
            if result:
                messages.extend(result)
        return messages


class IndentationsParser(AbstractParser):
    """
    Parser for E1** errors
    """

    def __init__(self):
        super().__init__()
        self.previous_indent = -1
        self.current_indent = -1
        self.expected_indent = -1

    def reset(self):
        """
        The method reset state
        :return: null
        """
        self.previous_indent = -1
        self.current_indent = -1
        self.expected_indent = -1

    def parse(self, line):
        """
        Description is the same as in the parent class
        :param line: str
        :return: list
        """
        messages = []
        if not self._check_if_docstrings(line):
            pattern = re.compile(r'(\s*)(\S*)')
            indent = pattern.match(line).group(1)
            if indent != line:
                if '\t' in indent:
                    if ' ' in indent:
                        messages.append((len(indent),  ErrorsEnum.E101))
                    else:
                        messages.append((len(indent), ErrorsEnum.W191))
                else:
                    if len(indent) % 4:
                        messages.append((len(indent), ErrorsEnum.E111))
                self.previous_indent = self.current_indent
                self.current_indent = len(indent.replace('\t', '    '))
                if -1 < self.expected_indent < self.current_indent:
                    messages.append((len(indent), ErrorsEnum.E113))
                elif (self.current_indent < self.expected_indent
                      != self.previous_indent > -1):
                    messages.append((len(indent), ErrorsEnum.E112))
                text = line[len(indent):]
                pattern = re.compile(r'.*:\s*$')
                if pattern.match(text):
                    self.expected_indent = self.current_indent+4
                else:
                    self.expected_indent = self.current_indent
                pattern = re.compile(r'.*(\(.*)')
                pattern2 = re.compile(r'.*\(.*(\(.*\))*\)')
                if pattern.match(text):
                    if not pattern2.match(text):
                        first = pattern.search(text).groups()[0]
                        if first == '(' or first == '[':
                            self.expected_indent += 4
                        else:
                            self.expected_indent = len(line)-len(first)

        return messages


class WhitespacesParser(AbstractParser):
    """
    Parser for E2** errors
    """

    def __init__(self):
        super().__init__()

    def parse(self, line):
        """
        Description is the same as in the parent class
        :param line: str
        :return: list
        """
        messages = []
        if not self._check_if_docstrings(line):
            pattern = re.compile(r'(\s*)(\S*)')
            indent = pattern.match(line).group(1)
            c_line = line[len(indent):]
            pattern = re.compile(r'(.*)(\'.*\')*\( .*')
            pattern2 = re.compile(r'.*(\'.*\( .*\').*')
            if pattern.match(c_line) and not pattern2.match(c_line):
                column = len(str(pattern.match(line).group(1)))
                messages.append((column, ErrorsEnum.E201))

            pattern = re.compile(r'(.*)(\'.*\')*\s\).*')
            pattern2 = re.compile(r'.*(\'.* \).*\').*')
            if pattern.match(c_line) and not pattern2.match(c_line):
                column = len(str(pattern.match(line).group(1)))
                messages.append((column, ErrorsEnum.E202))

            pattern = re.compile(r'(.*)(\'.*\')*\s:.*')
            pattern2 = re.compile(r'.*(\'.*\s:.*\').*')
            if pattern.match(c_line) and not pattern2.match(c_line):
                column = len(str(pattern.match(line).group(1)))
                messages.append((column, ErrorsEnum.E203))

            pattern = re.compile(r'(.*)(\'.*\')*\s\(.*')
            pattern2 = re.compile(r'\s*if|elif\s\(.*')
            pattern3 = re.compile(r'\S*\s=\s\(.*')
            pattern4 = re.compile(r'.*(\'.* \(.*\').*')
            if (pattern.match(c_line) and not pattern2.match(c_line)
               and not pattern3.match(c_line) and not pattern4.match(c_line)):
                column = len(str(pattern.match(line).group(1)))
                messages.append((column, ErrorsEnum.E211))

            pattern = re.compile(r'(.*),\S.*(\'.*\')*')
            pattern2 = re.compile(r'.*\'.*,.*\'.*')
            if pattern.match(c_line) and not pattern2.match(c_line):
                column = len(str(pattern.match(line).group(1)))
                messages.append((column, ErrorsEnum.E231))

            # pattern = re.compile('.*,\s\s.*')
            # if pattern.match(line):
            #     messages.append('E241')

            pattern = re.compile(r'((\'.*\')*\s*def\s\S*\(.*)(\s=)|(=\s)')
            if pattern.match(c_line):
                column = len(str(pattern.match(line).group(1)))
                messages.append((column, ErrorsEnum.E251))

            pattern = re.compile(r'((.*)\S*((\".*\")|(\'.*\'))*\S(\s||^#))#.*')
            if pattern.match(c_line):
                column = len(pattern.match(line).group(1))
                messages.append((column, ErrorsEnum.E261))

            pattern = re.compile(r'((.*)\S\S*((\".*\")|(\'.*\'))*\s*#)\S.*')
            if pattern.match(c_line):
                column = len(pattern.match(line).group(1))
                messages.append((column, ErrorsEnum.E262))

            pattern = re.compile(r'(\s*#)\S.*')
            if pattern.match(c_line):
                column = len(pattern.match(line).group(1))
                messages.append((column, ErrorsEnum.E265))

            pattern = re.compile(r'(\s*)##.*')
            if pattern.match(c_line):
                column = len(pattern.match(line).group(1))
                messages = [(column, ErrorsEnum.E266)]

        return messages


class BlankLinesParser(AbstractParser):
    """
    Parser for E3** errors
    """

    def __init__(self):
        super().__init__()
        self.started = False
        self.blank_lines = 0
        self.was_decorator = False

    def parse(self, line):
        """
        Description is the same as in the parent class
        :param line: str
        :return: list
        """
        messages = []
        if not self._check_if_docstrings(line):
            pattern = re.compile(r'^(\s)*$')
            if pattern.match(line):
                if self.was_decorator:
                    column = 0 if line == '' else \
                        len(pattern.match(line).group(1))
                    messages.append((column, ErrorsEnum.E304))
                else:
                    self.blank_lines += 1
            else:
                class_pattern = re.compile(r'^class\s.*')
                method_pattern = re.compile(r'^\s\s\s\sdef\s.*')
                decorator_pattern = re.compile(r'\s*@.*')
                if self.blank_lines > 2:
                    self.blank_lines = 0
                    messages.append((0, ErrorsEnum.E303))
                elif (class_pattern.match(line)
                      and 2 > self.blank_lines and self.started):
                    self.blank_lines = 0
                    messages.append((0, ErrorsEnum.E302))
                elif method_pattern.match(line) and self.started:
                    if self.blank_lines > 1:
                        messages.append((0, ErrorsEnum.E303))
                    elif self.blank_lines == 0:
                        messages.append((4, ErrorsEnum.E301))
                    self.blank_lines = 0
                if decorator_pattern.match(line):
                    self.was_decorator = True
                else:
                    self.was_decorator = False
                    self.blank_lines = 0
            self.started = True
        return messages


class ImportsParser(AbstractParser):
    """
    Parser for E4** errors
    """

    def __init__(self):
        super().__init__()

    def parse(self, line):
        """
        Description is the same as in the parent class
        :param line: str
        :return: list
        """
        messages = []
        if not self._check_if_docstrings(line):
            pattern = re.compile(r'(\s*import\s*.*,).*')
            if pattern.match(line):
                column = len(pattern.match(line).group(1))
                messages.append((column, ErrorsEnum.E401))
        return messages


class LineLengthParser(AbstractParser):
    """
    Parser for E5** errors
    """

    def __init__(self):
        super().__init__()

    def parse(self, line):
        """
        Description is the same as in the parent class
        :param line: str
        :return: list
        """
        messages = []
        if not self._check_if_docstrings(line):
            pattern = re.compile(r'(.*)\((\'.*\')*(\(.*\))*(.*)\\\s*')
            pattern2 = re.compile(r'.*(\'.*\\.*\').*')
            if len(line) > 79:
                messages.append((79, ErrorsEnum.E501))
            if pattern.match(line) and not pattern2.match(line):
                s = pattern.match(line).groups()
                column = len(str(pattern.match(line).group(1))
                             + str(pattern.match(line).group(4)))
                messages.append((column, ErrorsEnum.E502))
        return messages
