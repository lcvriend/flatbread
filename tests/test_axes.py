import unittest

import pandas as pd

import flatbread.build.test as test
import flatbread.config as config
import flatbread.axes as axes


class TestGetAxisNumber_Validation(unittest.TestCase):
    def test_non_existant(self):
        self.assertRaises(AssertionError, axes._get_axis_number, 'squid')


class TestAddCategory_CategoricalIndexSimple(unittest.TestCase):
    def setUp(self):
        self.idx = pd._testing.makeCategoricalIndex()

    def test_add_category(self):
        left = axes.add_category(self.idx, 'squid')
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
        left = axes.add_category(self.idx, 'squid', level=1).levels[1]
        right = pd.CategoricalIndex(
            self.cat.add_categories('squid'), name='C_l1')
        pd._testing.assert_index_equal(left, right)


class TestGetOrderedLabels(unittest.TestCase):
    def setUp(self):
        self.na_rep = config.get_value('aggregation', 'na_rep')

        categories = {
            key:[self.na_rep if val is None else val for val in values]
            for key, values in test.CATEGORIES.items()
        }

        self.taste = [i for i in test.CATEGORIES['taste'] if i is not None]
        self.touch = [i for i in test.CATEGORIES['touch'] if i is not None]

        kwargs = dict(
            columns = 'taste',
            index   = ['smell', 'touch'],
            aggfunc = 'size'
        )

        self.df = test.dataset(
            seed='squid',
            categories=categories
        ).pivot_table(**kwargs)
        self.df_cats = test.dataset(
            categories=categories,
            to_categories=True,
        ).pivot_table(**kwargs)

    def test_labels_from_single_first(self):
        axis = self.df.columns
        result = axes._get_ordered_labels(axis, 0, self.na_rep, 'first')
        expected = self.taste.copy()
        expected.sort()
        expected.insert(0, '-')
        expected = pd.Index(expected)
        self.assertTrue(result.equals(expected))

    def test_labels_from_single_last(self):
        axis = self.df.columns
        result = axes._get_ordered_labels(axis, 0, self.na_rep, 'last')
        expected = self.taste.copy()
        expected.sort()
        expected.append('-')
        expected = pd.Index(expected)
        self.assertTrue(result.equals(expected))

    def test_labels_from_single_categorical_first(self):
        axis = self.df_cats.columns
        result = axes._get_ordered_labels(axis, 0, self.na_rep, 'first')
        expected = self.taste.copy()
        expected.sort()
        expected.insert(0, '-')
        expected = pd.Index(expected)
        self.assertTrue(result.equals(expected))

    def test_labels_from_single_categorical_last(self):
        axis = self.df_cats.columns
        result = axes._get_ordered_labels(axis, 0, self.na_rep, 'last')
        expected = self.taste.copy()
        expected.append('-')
        expected = pd.Index(expected)
        self.assertTrue(result.equals(expected))

    def test_labels_from_multi_first(self):
        axis = self.df.index
        result = axes._get_ordered_labels(axis, 1, self.na_rep, 'first')
        expected = self.touch.copy()
        expected.sort()
        expected.insert(0, '-')
        expected = pd.Index(expected)
        self.assertTrue(result.equals(expected))

    def test_labels_from_multi_last(self):
        axis = self.df.index
        result = axes._get_ordered_labels(axis, 1, self.na_rep, 'last')
        expected = self.touch.copy()
        expected.sort()
        expected.append('-')
        expected = pd.Index(expected)
        self.assertTrue(result.equals(expected))
