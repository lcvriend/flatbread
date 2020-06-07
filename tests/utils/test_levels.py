import unittest
import pandas as pd
import pita.utils.levels as levels


class TestGetLevels_MultiIndex(unittest.TestCase):
    def setUp(self):
        self.index = pd._testing.makeMultiIndex(names=['A', 'B'])

    def test_get_level_from_negative_index(self):
        left = levels.get_absolute_level(self.index, level=-1)
        right = 1
        self.assertTrue(left == right)

    def test_get_level_from_positive_index(self):
        left = levels.get_absolute_level(self.index, level=1)
        right = 1
        self.assertTrue(left == right)

    def test_get_level_from_level_name(self):
        left = levels.get_level_from_alias(self.index, level='B')
        right = 1
        self.assertTrue(left == right)

    def test_get_level_from_non_existent_level_name(self):
        self.assertRaises(
            KeyError,
            levels.get_level_from_alias,
            self.index,
            level='squid')

    def test_validation_of_negative_index_out_of_range(self):
        self.assertRaises(
            IndexError,
            levels.validate_level,
            self.index,
            level=-3)

    def test_validation_of_positive_index_out_of_range(self):
        self.assertRaises(
            IndexError,
            levels.validate_level,
            self.index,
            level=3)


class TestValidateForOperationWithin_Simple(unittest.TestCase):
    def setUp(self):
        self.index = pd._testing.makeStringIndex()

    def test_validation_level_0(self):
        self.assertRaises(
            ValueError,
            levels.validate_index_for_within_operations,
            self.index,
            level=0)


class TestValidateForOperationWithin_MultiIndex(unittest.TestCase):
    def setUp(self):
        self.index = pd._testing.makeMultiIndex(names=['A', 'B'])

    def test_validation_level_0(self):
        self.assertRaises(
            ValueError,
            levels.validate_index_for_within_operations,
            self.index,
            level=0)


if __name__ == '__main__':
    unittest.main()
