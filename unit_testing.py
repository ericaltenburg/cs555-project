import unittest
from gedcomParser import *
from datetime import *
from dateutil.parser import parse

class TestGedcome(unittest.TestCase):

    def test_before_current_date(self):
        self.assertEqual(before_current_date("01-01-2040", "Julie", "I01", "Birth"),
                         "Error US01: Birth date of Julie(I01) occurs before the current date.")
    def test_marriage_before_birth(self):
        self.assertEqual(marriage_before_birth("01-01-1900", "01-01-2000", "Julie", "I01"),
                         "Error US02: Marriage date of Julie(I01) occurs before their birth date.")

if __name__ == '__main__':
    unittest.main()
