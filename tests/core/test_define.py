import unittest

import pandas as pd

import flatbread.core.axes.define as define


class TestAddCategory_CategoricalIndexSimple(unittest.TestCase):
    def setUp(self):
        self.idx = pd._testing.makeCategoricalIndex()

    def test_add_category(self):
        left = define.add_category(self.idx, 'squid')
        right = self.idx.add_categories('squid')
        pd._testing.assert_index_equal(left, right)


class TestAddCategory_CategoricalIndexMulti(unittest.TestCase):
    def setUp(self):
        self.cat = pd.Categorical(['a', 'b', 'c'])
        df = pd.DataFrame.from_records({
            'C_l0': ['A', 'B', 'C'],
            'C_l1': self.cat})
        self.idx = pd.MultiIndex.from_frame(df)

    def test_add_category(self):
        left = define.add_category(self.idx, 'squid', level=1).levels[1]
        right = pd.CategoricalIndex(
            self.cat.add_categories('squid'), name='C_l1')
        pd._testing.assert_index_equal(left, right)
