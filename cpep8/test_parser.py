"""
Unit test module for logic testing
"""
__author__ = 'Skipper'
from pep_parser import *
import unittest


class TestIndentationsParser(unittest.TestCase):

    def setUp(self):
        self.parser = IndentationsParser()

    def test_e101(self):
        self.parser.reset()
        line = '\t    a = 6 + 50'
        result = self.parser.parse(line)
        self.assertEqual(result, [(5, ErrorsEnum.E101)])

    def test_e111(self):
        self.parser.reset()
        line = '     a = 6 + 50'
        result = self.parser.parse(line)
        self.assertEqual(result, [(5, ErrorsEnum.E111)])

    def test_e112(self):
        self.parser.reset()
        messages = []
        lines = ['    if self.expected_indent < self.current_indent:',
                 '    if self.expected_indent < self.current_indent:']
        for line in lines:
            result = self.parser.parse(line)
            if result:
                messages.append(result)
        self.assertEqual(messages, [[(4, ErrorsEnum.E112)]])

    def test_e113(self):
        self.parser.reset()
        messages = []
        lines = ['    self.expected_indent = self.current_indent',
                 '        self.expected_indent += self.current_indent']
        for line in lines:
            result = self.parser.parse(line)
            if result:
                messages.append(result)
        self.assertEqual(messages, [[(8, ErrorsEnum.E113)]])


class TestWhitespacesParser(unittest.TestCase):

    def setUp(self):
        self.parser = WhitespacesParser()

    def test_e201(self):
        line = 'class TestWhitespacesParser( unittest.TestCase):'
        result = self.parser.parse(line)
        self.assertEqual(result, [(27, ErrorsEnum.E201)])

    def test_e202(self):
        line = 'TestWhitespacesParser(unittest.TestCase )'
        result = self.parser.parse(line)
        self.assertEqual(result, [(39, ErrorsEnum.E202)])

    def test_e203(self):
        line = 'a = {1 : 25, 2 :34}'
        result = self.parser.parse(line)
        self.assertEqual(result, [(14, ErrorsEnum.E203)])

    def test_e211(self):
        line = 'TestWhitespacesParser (unittest.TestCase)'
        line2 = 'if pattern.match(line) and not pattern2.match(line):'
        result = self.parser.parse(line)
        self.assertEqual(result, [(21, ErrorsEnum.E211)])
        result = self.parser.parse(line2)
        self.assertEqual(result, [])

    def test_e231(self):
        line = 'a = 1,2, 3'
        result = self.parser.parse(line)
        self.assertEqual(result, [(5, ErrorsEnum.E231)])

    # def test_e241(self):
    #     line = 'a = 1,2,  3'
    #     result = self.parser.parse(line)
    #     self.assertEqual(result, ['E241'])

    def test_e251(self):
        line = '    def setUp(self, number = 0):'
        result = self.parser.parse(line)
        self.assertEqual(result, [(26, ErrorsEnum.E251)])

    def test_e261(self):
        line = 'a = 5 # blabla'
        result = self.parser.parse(line)
        self.assertEqual(result, [(6, ErrorsEnum.E261)])

    def test_e262(self):
        line = 'a = 5  #blabla'
        result = self.parser.parse(line)
        self.assertEqual(result, [(8, ErrorsEnum.E262)])

    def test_e265(self):
        line = '    #blabla'
        result = self.parser.parse(line)
        self.assertEqual(result, [(5, ErrorsEnum.E265)])

    def test_e266(self):
        line = '    ## blabla'
        result = self.parser.parse(line)
        self.assertEqual(result, [(4, ErrorsEnum.E266)])


class TestBlankLinesParser(unittest.TestCase):

    def setUp(self):
        self.parser = BlankLinesParser()

    def test_e301(self):
        sources = \
            'class TestBlankLinesParser(unittest.TestCase):\n    def setUp(s'\
            + 'elf):\n        pass\n    def setUp(self):'
        sources = sources.split('\n')
        messages = []
        for line in sources:
            result = self.parser.parse(line)
            if result:
                messages.append(result)
        self.assertEqual(messages, [[(4, ErrorsEnum.E301)],
                                    [(4, ErrorsEnum.E301)]])

    def test_e302(self):
        sources = \
            'main()\nclass TestBlankLinesParser(unittest.TestCase):'\
            + '\n\n    def setUp(self):\n        pass\n\n    def setUp(self):'
        sources = sources.split('\n')
        messages = []
        for line in sources:
            result = self.parser.parse(line)
            if result:
                messages.append(result)
        self.assertEqual(messages, [[(0, ErrorsEnum.E302)]])

    def test_e303(self):
        sources = [
            'class TestBlankLinesParser(unittest.TestCase):',
            '',
            '',
            '    def setUp(self):',
            '        pass']
        messages = []
        for line in sources:
            result = self.parser.parse(line)
            if result:
                messages.append(result)
        self.assertEqual(messages, [[(0, ErrorsEnum.E303)]])

    def test_e304(self):
        sources = [
            'class TestBlankLinesParser(unittest.TestCase):',
            '',
            '    @decorator',
            '',
            '    def setUp(self):',
            '        pass']
        messages = []
        for line in sources:
            result = self.parser.parse(line)
            if result:
                messages.append(result)
        self.assertEqual(messages, [[(0, ErrorsEnum.E304)]])


class TestImportsParser(unittest.TestCase):

    def setUp(self):
        self.parser = ImportsParser()

    def test_401(self):
        line = 'import a, b, c'
        result = self.parser.parse(line)
        self.assertEqual(result, [(12, ErrorsEnum.E401)])


class TestLineLengthParser(unittest.TestCase):

    def setUp(self):
        self.parser = LineLengthParser()

    def test_e501(self):
        line = 'zxcvasdqweqweqweqweqweqweqweqweqweqwewqe'\
               + 'qweqweqweqweqweqweqweqweqweqweqweqweqweqwe'
        result = self.parser.parse(line)
        self.assertEqual(result, [(79, ErrorsEnum.E501)])

    def test_e502(self):
        line = 'a = (5 + 3 \\'
        result = self.parser.parse(line)
        self.assertEqual(result, [(10, ErrorsEnum.E502)])


if __name__ == '__main__':
    unittest.main()
