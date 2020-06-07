import unittest
from random import randint

import pandas as pd

import flatbread


class TestTotalsAdd_DataFrameSimple(unittest.TestCase):
    def setUp(self):
        self.totals_name = flatbread.agg.globals.TOTALS_NAME
        self.df = pd._testing.makeDataFrame().head(5)

    def test_add_rows(self):
        s = flatbread.agg.totals.add(self.df, axis=0).loc[self.totals_name]
        self.assertTrue(s.equals(self.df.sum()))

    def test_add_cols(self):
        s = flatbread.agg.totals.add(self.df, axis=1).loc[:, self.totals_name]
        self.assertTrue(s.equals(self.df.sum(axis=1)))

    def test_add_both(self):
        v = (flatbread.agg.totals.add(self.df, axis=2)
            .loc[self.totals_name, self.totals_name])
        self.assertTrue(v == self.df.sum().sum())


class TestTotalsAdd_DataFrameCategorical(unittest.TestCase):
    def setUp(self):
        self.totals_name = flatbread.agg.globals.TOTALS_NAME
        df = pd._testing.makeDataFrame().head(5)
        df.columns = pd.Categorical(df.columns)
        df.index = pd.Categorical(df.index)
        self.df = df

    def test_add_rows(self):
        s = flatbread.agg.totals.add(self.df, axis=0).loc[self.totals_name]
        self.assertTrue(s.equals(self.df.sum()))

    def test_add_cols(self):
        s = flatbread.agg.totals.add(self.df, axis=1).loc[:, self.totals_name]
        self.assertTrue(s.equals(self.df.sum(axis=1)))

    def test_add_both(self):
        v = (flatbread.agg.totals.add(self.df, axis=2)
            .loc[self.totals_name, self.totals_name])
        self.assertTrue(v == self.df.sum().sum())


class TestTotalsAdd_DataFrameMultiIndex(unittest.TestCase):
    def setUp(self):
        self.df = pd._testing.makeCustomDataframe(
            nrows=7,
            ncols=4,
            data_gen_f=lambda r,c:randint(1,100),
            c_idx_nlevels=2,
            r_idx_nlevels=3,
            c_ndupe_l=[2,1],
            r_ndupe_l=[4,2,1])

    def test_add_rows(self):
        s = flatbread.agg.totals.add(self.df, axis=0).iloc[-1]
        self.assertTrue(s.equals(self.df.sum()))

    def test_add_cols(self):
        s = flatbread.agg.totals.add(self.df, axis=1).iloc[:, -1]
        self.assertTrue(s.equals(self.df.sum(axis=1)))

    def test_add_both(self):
        v = (flatbread.agg.totals.add(self.df, axis=2).iloc[-1, -1])
        self.assertTrue(v == self.df.sum().sum())

    def test_add_rows_within(self):
        left = (
            flatbread.agg.totals.add(self.df, level=-1)
            .xs(flatbread.agg.globals.SUBTOTALS_NAME, level=-1)
            .values)
        right = self.df.groupby(level=-2).sum().values
        comparison = (left == right).all()
        self.assertTrue(comparison)

    def test_add_cols_within(self):
        left = (
            flatbread.agg.totals.add(self.df, axis=1, level=1)
            .xs(flatbread.agg.globals.SUBTOTALS_NAME, axis=1, level=1)
            .values)
        right = self.df.groupby(level=0, axis=1).sum().values
        comparison = (left == right).all()
        self.assertTrue(comparison)


if __name__ == '__main__':
    unittest.main()
