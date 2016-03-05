"""
Unit test for "resolver" module
"""
__author__ = 'Skipper'
from resolver import Resolver
import unittest


class TestResolver(unittest.TestCase):
    """
    Test class for Resolver
    """
    def setUp(self):
        self.resolver = Resolver()

    def testARecords(self):
        reference_a_record = [(1, '31.170.165.34')]
        test_a_record = self.resolver.resolve('eur.al')
        self.assertEqual(reference_a_record, test_a_record)

    def testNoResponse(self):
        reference_no_response = Resolver.NO_RESPONSE
        self.resolver.port = 65000
        test = self.resolver.resolve('eur.al')
        self.assertEqual(reference_no_response, test)
        self.resolver.port = 53

    def testNotFound(self):
        reference = Resolver.NAME_NOT_FOUND
        test = self.resolver.resolve('opsidjgsdkjf.paris')
        self.assertEqual(reference, test)

    def testCNameRecord(self):
        reference = 5, 'dijkstra.urgu.org'
        test = self.resolver.resolve('anytask.urgu.org')
        self.assertEqual(reference, test[0])

    def testRecursion(self):
        self.resolver = Resolver('198.41.0.4')
        reference_a_record = [(1, '31.170.165.34')]
        test_a_record = self.resolver.resolve('eur.al')
        self.assertEqual(reference_a_record, test_a_record)

if __name__ == "__main__":
    unittest.main()
