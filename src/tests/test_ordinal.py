import unittest

from elech_tools.utils.ordinal import ordinal


class TestOrdinal(unittest.TestCase):
    def test_ordinal(self):
        self.assertEqual(ordinal(1), "1st")
        self.assertEqual(ordinal(2), "2nd")
        self.assertEqual(ordinal(3), "3rd")
        self.assertEqual(ordinal(4), "4th")
        self.assertEqual(ordinal(5), "5th")
        self.assertEqual(ordinal(6), "6th")
        self.assertEqual(ordinal(7), "7th")
        self.assertEqual(ordinal(8), "8th")
        self.assertEqual(ordinal(9), "9th")
        self.assertEqual(ordinal(10), "10th")
        self.assertEqual(ordinal(11), "11th")
        self.assertEqual(ordinal(12), "12th")
        self.assertEqual(ordinal(13), "13th")
        self.assertEqual(ordinal(14), "14th")
        self.assertEqual(ordinal(20), "20th")
        self.assertEqual(ordinal(21), "21st")
        self.assertEqual(ordinal(22), "22nd")
        self.assertEqual(ordinal(23), "23rd")
        self.assertEqual(ordinal(24), "24th")
