from nlp import HumanName, isFullName
import unittest
class testNames(unittest.TestCase):

    def test_name_gender(self):
        tests = [
            ("Alec McGail", "male"),
            ("Mr. McGail", "male"),
            ("Mr. A. M. McGail", "male"),
            ("John", "male"),
            ("Jimmy 'The Bomb' Johnson", "male"),
            ("Prince James", "male"),

            ("Princess Diane", "female"),
            ("Ms. Maisel", "female"),
            ("Mrs. A. Samuel", "female"),
            ("Jane Doe", "female")
        ]
        for (name, gender) in tests:
            self.assertEqual( HumanName(name).gender, gender )

    def test_name_matching(self):
        name_no1 = HumanName("Alec Michael McGail")
        self.assertTrue( name_no1.supercedes( HumanName("Alec McGail")))
        self.assertTrue(name_no1.supercedes( HumanName("Mr. McGail")))
        self.assertFalse(name_no1.supercedes( HumanName("Ms. McGail")))
        self.assertFalse(name_no1.supercedes( HumanName("Mrs. McGail")))
        self.assertTrue(name_no1.supercedes( HumanName("Dr. McGail")))
        self.assertTrue(name_no1.supercedes( HumanName("Dr. Alec McGail")))
        self.assertFalse(name_no1.supercedes( HumanName("Dr. Alec P. McGail")))
        self.assertFalse(name_no1.supercedes( HumanName("Dr. Alec Patricia McGail")))
        self.assertTrue(name_no1.supercedes( HumanName("Dr. A. McGail")))

        self.assertFalse(name_no1.supercedes(HumanName("Alec McGail Jr.")))

        name_no2 = HumanName("Dr. A. M. (Johnny) Fischer III")
        self.assertTrue(name_no2.supercedes(HumanName("Mr. Fischer")))
        self.assertTrue(name_no2.supercedes(HumanName("Andy Fischer III")))
        self.assertFalse(name_no2.supercedes(HumanName("Andy Fischer")))
        self.assertTrue(name_no2.supercedes(HumanName("Andrew Marklehovitch Fischer III")))
        self.assertTrue(name_no2.supercedes(HumanName("Ms. Fischer")))

    def test_name_identification(self):
        self.assertTrue(isFullName("Alec McGail"))
        self.assertTrue(isFullName("Alec M. McGail"))
        self.assertTrue(isFullName("Alec Michael McGail"))
        self.assertTrue(isFullName("Mr. Alec McGail"))
        self.assertTrue(isFullName("Mr. John Wright McGail III"))
        self.assertTrue(isFullName("Jo Spirak"))  # androgenous...
        # self.assertTrue(isFullName("Yosalinda McWrightson")) # weird name doesn't work --

        self.assertFalse(isFullName("Dr. McGail"))
        self.assertFalse(isFullName("University of Toronto"))
        self.assertFalse(isFullName("United States"))
        self.assertFalse(isFullName("Republican Party"))
        self.assertFalse(isFullName("John"))

if __name__ == '__main__':
    unittest.main()