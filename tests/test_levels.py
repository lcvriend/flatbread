import unittest
import pandas as pd
import flatbread.levels as levels


class TestGetLevels_MultiIndex(unittest.TestCase):
    def setUp(self):
        self.index = pd._testing.makeMultiIndex(names=['A', 'B'])

    def test_get_level_from_negative_index(self):
        left = levels._get_absolute_level(self.index, level=-1)
        right = 1
        self.assertTrue(left == right)

    def test_get_level_from_positive_index(self):
        left = levels._get_absolute_level(self.index, level=1)
        right = 1
        self.assertTrue(left == right)

    def test_get_level_from_level_name(self):
        left = levels._get_level_from_name(self.index, level_name='B')
        right = 1
        self.assertTrue(left == right)

    def test_get_level_from_non_existent_level_name(self):
        df = pd.DataFrame(index=self.index)
        self.assertRaises(
            KeyError,
            levels._get_level_number,
            df,
            axis=0,
            level='squid'
        )

    def test_validation_of_negative_index_out_of_range(self):
        self.assertRaises(
            IndexError,
            levels._validate_level,
            self.index,
            level=-3
        )

    def test_validation_of_positive_index_out_of_range(self):
        self.assertRaises(
            IndexError,
            levels._validate_level,
            self.index,
            level=3
        )


class TestValidateForOperationWithin_Simple(unittest.TestCase):
    def setUp(self):
        index = pd._testing.makeStringIndex()
        self.df = pd.DataFrame(index=index)

    def test_validation_level_0(self):
        self.assertRaises(
            ValueError,
            levels._validate_index_for_within_operations,
            self.df,
            level=0
        )


class TestValidateForOperationWithin_MultiIndex(unittest.TestCase):
    def setUp(self):
        index = pd._testing.makeMultiIndex(names=['A', 'B'])
        self.df = pd.DataFrame(index=index)

    def test_validation_level_0(self):
        self.assertRaises(
            ValueError,
            levels._validate_index_for_within_operations,
            self.df,
            level=0
        )


if __name__ == '__main__':
    unittest.main()
