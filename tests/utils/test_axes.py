import unittest
import flatbread.utils.axes as axes


class TestGetAxisNumber_Validation(unittest.TestCase):
    def test_non_existant(self):
        self.assertRaises(AssertionError, axes.get_axis_number, 'squid')


if __name__ == '__main__':
    unittest.main()
