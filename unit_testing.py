import unittest
from gedcomParser import *
from datetime import *
from dateutil.parser import parse

class TestGedcom(unittest.TestCase):

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
	def test_no_bigamy1(self):
		self.assertEqual(no_bigamy("01-01-1990", "01-01-1999", "01-01-2000", "Steel", "I11", "16"), 
						"Anomaly US11: Marriage of Steel(I11) occurred during another marriage (there is bigamy) on Families table line 16.")
	def test_no_bigamy2(self):
		self.assertEqual(no_bigamy("01-01-1990", "01-01-1999", "N/A", "Manny", "I18", "19"), 
						"Anomaly US11: Marriage of Manny(I18) occurred during another marriage (there is bigamy) on Families table line 19.")
	def test_parent_too_old1(self):
		self.assertEqual(parent_too_old("01-02-2000", "01-01-1900", "Jackie", "I12", "F", "I01", "17"), 
						"Anomaly US12: Jackie(I12) is a mother who is 100 (more than 60) years older than her child(I01) on line 17.")
	def test_parent_too_old2(self):
		self.assertEqual(parent_too_old("02-02-2000", "01-01-1919", "Jacob", "I12", "M", "I01", "17"), 
						"Anomaly US12: Jacob(I12) is a father who is 81 (more than 80) years older than his child(I01) on line 17.")
	def test_more_than_15_siblings(self):
		self.assertEqual(more_than_15_siblings(16, "F06", "128"), "Anomaly US15: Family (F06) has more than 15 siblings on line 128.")
	def test_different_last_names(self):
		self.assertEqual(different_last_names("Altenburg", "Chasnov", "I09", "128"), "Anomaly US16: Chasnov (I09) does not have the same name as their father (Altenburg) on line 128.")
	def test_birth_before_parents_death_mother(self):
		self.assertEqual(birth_before_parents_death("02-02-2000", "Suzy Smith", "I02", "01-01-2000", True, "128"), "Error US09: Birth of Suzy Smith(I02) is after the death of their mother on line 128.")
	def test_birth_before_parents_death_father(self):
		self.assertEqual(birth_before_parents_death("11-11-2000", "Suzy Smith", "I02", "01-01-2000", False, "128"), "Error US09: Birth of Suzy Smith(I02) is after 9 months after the death of their father on line 128.")
	def test_marriage_after_14(self):
		self.assertEqual(marriage_after_14("I02", "Suzy Smith", "01-01-2005", "02-02-2000", "128"),
						"Error US10: Birth of Suzy Smith(I02) is less than 14 years before their marriage date on line 128.")

	def test_siblings_spacing(self):
		self.assertEqual(siblings_spacing(["02-15-1968", "02-16-1968", "03-29-1969", "05-29-1969"], 20, 140),
						"Anomaly US13: Family 20 has children with invalid age differences on line 140.")
	def test_multiple_births(self):
		self.assertEqual(multiple_births(["03-23-1966", "03-23-1966", "02-15-1968","02-15-1968", "02-15-1968", "02-16-1968", "02-16-1968"], 21, 210), 
						"Anomaly US14: Family 21 has more than 5 children born at the same time on line 210.")
	def test_no_descendant_marriage(self):
		self.assertEqual(no_descendant_marriage("I01", "John Doe", "I03", "211"), "Error US17: Parent John Doe(I01) is married to their child (I03) on line 211.")
	def test_no_sibling_marriage(self):
		self.assertEqual(no_sibling_marriage("I01", "John Doe", "I02", "Jane Doe", "211"), "Error US18: Sibling John Doe(I01) is married to their sibling Jane Doe(I02) on line 211.")  
	def test_incorrect_gender_husb(self):
		self.assertEqual(incorrect_gender_husb("HUSB", "Betty Green", "I14", "F", "88"), "Error US21: Husband role and gender are incorrect for Betty Green (I14) on Individual List line 88.")
	def test_incorrect_gender_wife(self):
		self.assertEqual(incorrect_gender_wife("WIFE", "Bobby Yellow", "I17", "M", "74"), "Error US21: Wife role and gender are incorrect for Bobby Yellow (I17) on Individual List line 74.")
	def test_unique_id(self):
		self.assertEqual(unique_id("INDI", "I2", "Zack Martin", "34"), "Error US22: Individual (Zack Martin) does not have a unique ID (I2) on Individuals List line 34.")
	def test_unique_id(self):
		self.assertEqual(unique_id("FAM", "I6", "Cody Martin", "43"), "Error US22: Family with husband Cody Martin does not have a unique ID (I6) on Families List line 43.")
	def test_same_name_birthdate(self):
		self.assertEqual(same_name_birthdate("Eric Altenburg", "Eric Altenburg", "04-14-1999", "04-14-1999", "I01", "I02", "123"), "Error US23: Individual with ID I01 has the same name and birth date as I02 on Individual List Line 123.")
	def test_recent_births(self):
		self.assertEqual(recent_births(parse("13 APR 2021"), "Sam Case", "I35", "390"), "Info US35: Sam Case (I35) was born within the past 30 days on 2021-04-13 00:00:00 on line 390.")
	def test_recent_deaths(self):
		self.assertEqual(recent_deaths(parse("13 APR 2021"), "Pat Smith", "I28", "122"), "Info US36: Pat Smith (I28) has died within the past 30 days on 2021-04-13 00:00:00 on line 122.")
	def test_same_spouse_name_marr_date(self):
		existing_fam_dict = {
			"Husband Name" : "Eric Altenburg",
			"Wife Name" : "Erica Altenburg",
			"Married" : "04-14-1999",
			"ID" : "@F1@ "
		}
		new_fam_dict = {
			"Husband Name" : "Eric Altenburg",
			"Wife Name" : "Erica Altenburg",
			"Married" : "04-14-1999",
			"ID" : "@F2@ "
		}
		self.assertEqual(same_spouse_name_marr_date(existing_fam_dict, new_fam_dict, "123"), "Error US24: Family @F2@ has the same spouse names and marriage date as family @F1@ on Families List line 123.")
	def test_unique_first_family_names(self):
		self.assertEqual(unique_first_family_names({"Jane Doe":["3 AUG 2001","3 AUG 2001 "]}, "126"), "Anomaly US25: There are more than one instance of Jane Doe born on 3 AUG 2001 on line 126.")
	def test_check_consistency(self):
		self.assertEqual(check_consistency(4,5), "Error US26: Individual entries: 4 do not match Family entries: 5.")
	def test_list_single_over_30_fail(self):
		self.assertNotEqual(list_single_over_30(40, "@F3@", "Eric Altenburg", "@I7@", "123"), "Info US31: Eric Altenburg (@I7@) is over 30 years old at 40 and not married on line 123.")
	def test_list_single_over_30_pass(self):
		self.assertEqual(list_single_over_30(40, "N/A", "Eric Altenburg", "@I7@", "123"), "Info US31: Eric Altenburg (@I7@) is over 30 years old at 40 and not married on line 123.")
	def test_list_all_multiple_births(self):
		self.assertNotEqual(list_all_multiple_births(1, "F1", "123"), "Info US32: Family F1 has multiple births (1) on line 123.")
	def test_list_all_multiple_births_pass(self):
		self.assertEqual(list_all_multiple_births(2, "F1", "123"), "Info US32: Family F1 has multiple births (2) on line 123.")
if __name__ == '__main__':
	unittest.main()
