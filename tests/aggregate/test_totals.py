import unittest
from random import randint

import pandas as pd

import flatbread


class TestTotalsAdd_DataFrameSimple(unittest.TestCase):
    def setUp(self):
        self.totals_name = flatbread.agg.set_value('totals_name')
        self.df = pd._testing.makeDataFrame().head(5)

    def test_add_rows(self):
        s = flatbread.totals.add(self.df, axis=0).loc[self.totals_name]
        self.assertTrue(s.equals(self.df.sum()))

    def test_add_cols(self):
        s = flatbread.totals.add(self.df, axis=1).loc[:, self.totals_name]
        self.assertTrue(s.equals(self.df.sum(axis=1)))

    def test_add_both(self):
        v = flatbread.totals.add(self.df, axis=2).loc[
            self.totals_name, self.totals_name
        ]
        self.assertTrue(v == self.df.sum().sum())


class TestTotalsAdd_DataFrameCategorical(unittest.TestCase):
    def setUp(self):
        self.totals_name = flatbread.agg.set_value('totals_name')
        df = pd._testing.makeDataFrame().head(5)
        df.columns = pd.Categorical(df.columns)
        df.index = pd.Categorical(df.index)
        self.df = df

    def test_add_rows(self):
        s = flatbread.totals.add(self.df, axis=0).loc[self.totals_name]
        self.assertTrue(s.equals(self.df.sum()))

    def test_add_cols(self):
        s = flatbread.totals.add(self.df, axis=1).loc[:, self.totals_name]
        self.assertTrue(s.equals(self.df.sum(axis=1)))

    def test_add_both(self):
        v = flatbread.totals.add(self.df, axis=2).loc[
            self.totals_name, self.totals_name
        ]
        self.assertTrue(v == self.df.sum().sum())


class TestTotalsAdd_DataFrameMultiIndex(unittest.TestCase):
    def setUp(self):
        self.df = pd._testing.makeCustomDataframe(
            nrows=7,
            ncols=4,
            data_gen_f=lambda r, c: randint(1, 100),
            c_idx_nlevels=2,
            r_idx_nlevels=3,
            c_ndupe_l=[2, 1],
            r_ndupe_l=[4, 2, 1],
        )

    def test_add_rows(self):
        s = flatbread.totals.add(self.df, axis=0).iloc[-1]
        self.assertTrue(s.equals(self.df.sum()))

    def test_add_cols(self):
        s = flatbread.totals.add(self.df, axis=1).iloc[:, -1]
        self.assertTrue(s.equals(self.df.sum(axis=1)))

    def test_add_both(self):
        v = flatbread.totals.add(self.df, axis=2).iloc[-1, -1]
        self.assertTrue(v == self.df.sum().sum())

    def test_add_rows_within(self):
        left = (
            flatbread.totals.add(self.df, level=-1)
            .xs(flatbread.agg.set_value('subtotals_name'), level=-1)
            .values
        )
        right = self.df.groupby(level=-2).sum().values
        comparison = (left == right).all()
        self.assertTrue(comparison)

    def test_add_cols_within(self):
        left = (
            flatbread.totals.add(self.df, axis=1, level=1)
            .xs(flatbread.agg.set_value('subtotals_name'), axis=1, level=1)
            .values
        )
        right = self.df.groupby(level=0, axis=1).sum().values
        comparison = (left == right).all()
        self.assertTrue(comparison)

    def test_commutative_property(self):
        left = (
            self.df
            .pipe(flatbread.totals.add)
            .pipe(flatbread.totals.add, level=1)
        )
        right = (
            self.df
            .pipe(flatbread.totals.add, level=1)
            .pipe(flatbread.totals.add)
        )
        self.assertTrue(left.equals(right))


if __name__ == "__main__":
    unittest.main()
