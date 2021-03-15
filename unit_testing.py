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
    def test_death_before_birth(self):
        self.assertEqual(death_before_birth("01-01-1999", "01-01-2000", "Sam", "I02"),
                         "Error US03: Death date of Sam(I02) occurs before their birth date.")
    def test_divorce_before_marriage(self):
        self.assertEqual(divorce_before_marriage("01-01-1999", "01-01-2000", "Jack", "I02"),
                         "Error US04: Divorce date of Jack(I02) occurs before their marriage date.")                     
    def test_greater_than_150(self):
        self.assertEqual(greater_than_150("150", "Jill", "I09"), "Error US07: Age of Jill(I09) is not less than 150.")
    def test_birth_before_marriage(self):
        self.assertEqual(birth_before_marriage("01-01-1999", "01-01-2000", "N/A", "Jim Beam", "I03", "F04"), "Anomaly US08: Birth date of Jim Beam(I03) occurs before the marriage date of their parents in Family F04.")
    def test_birth_before_marriage_divorce(self):
        self.assertEqual(birth_before_marriage("01-01-1999", "01-01-1990", "01-01-1998", "Jim Beam", "I03", "F04"), "Anomaly US08: Birth date of Jim Beam(I03) occurs 9 months after the divorce date of their parents in Family F04.")
if __name__ == '__main__':
    unittest.main()
