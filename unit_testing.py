import unittest
from gedcomParser import *
from datetime import *
from dateutil.parser import parse

class TestGedcome(unittest.TestCase):

    def test_before_current_date(self):
        self.assertEqual(before_current_date("01-01-2040", "Julie", "I01", "Birth", "1"),
                         "Error US01: Birth date of Julie(I01) occurs before the current date on line 1.")
    def test_marriage_before_birth(self):
        self.assertEqual(marriage_before_birth("01-01-1900", "01-01-2000", "Julie", "I01", "2"),
                         "Error US02: Marriage date of Julie(I01) occurs before their birth date on line 2.")
    def test_death_before_birth(self):
        self.assertEqual(death_before_birth("01-01-1999", "01-01-2000", "Sam", "I02", "3"),
                         "Error US03: Death date of Sam(I02) occurs before their birth date on line 3.")
    def test_divorce_before_marriage(self):
        self.assertEqual(divorce_before_marriage("01-01-1999", "01-01-2000", "Jack", "I02", "4"),
                         "Error US04: Divorce date of Jack(I02) occurs before their marriage date on line 4.")                     
    def test_death_before_marriage(self):
        self.assertEqual(death_before_marriage("01-01-2000", "01-01-2001", "John", "I07", "11"),
                         "Error US05: Death date of John(I07) occurs before their marriage date on line 11.")
    def test_death_before_divorce(self):
        self.assertEqual(death_before_divorce("01-01-2000", "01-01-2002", "John", "I07", "12"),
                         "Error US06: Death date of John(I07) occurs before their divorce date on line 12.")
    def test_greater_than_150(self):
        self.assertEqual(greater_than_150("150", "Jill", "I09", "5"), "Error US07: Age of Jill(I09) is not less than 150 on line 5.")
    def test_birth_before_marriage(self):
        self.assertEqual(birth_before_marriage("01-01-1999", "01-01-2000", "N/A", "Jim Beam", "I03", "F04", "6"), "Anomaly US08: Birth date of Jim Beam(I03) occurs before the marriage date of their parents in Family F04 on line 6.")
    def test_birth_before_marriage_divorce(self):
        self.assertEqual(birth_before_marriage("01-01-1999", "01-01-1990", "01-01-1998", "Jim Beam", "I03", "F04", "7"), "Anomaly US08: Birth date of Jim Beam(I03) occurs after 9 months from the divorce date of their parents in Family F04 on line 7.")
if __name__ == '__main__':
    unittest.main()
