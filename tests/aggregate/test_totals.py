import unittest
from random import randint

import pandas as pd

import flatbread


class TestTotalsAdd_DataFrameSimple(unittest.TestCase):
    def setUp(self):
        self.totals_name = flatbread.agg.get_value('totals_name')
        self.df = pd._testing.makeCustomDataframe(
            nrows=5,
            ncols=4,
            data_gen_f=lambda r,c:randint(1,100),
        )

    def test_add_column_total_to_rows(self):
        s = flatbread.totals.add(self.df, axis=0).loc[self.totals_name]
        self.assertTrue(s.equals(self.df.sum()))

    def test_add_row_total_to_cols(self):
        s = flatbread.totals.add(self.df, axis=1).loc[:, self.totals_name]
        self.assertTrue(s.equals(self.df.sum(axis=1)))

    def test_add_both(self):
        v = flatbread.totals.add(self.df, axis=2).loc[
            self.totals_name, self.totals_name
        ]
        self.assertTrue(v == self.df.sum().sum())

    def test_preserve_axis_names(self):
        r1 = flatbread.totals.add(self.df)
        r2 = flatbread.totals.add(self.df, axis=1)
        self.assertEqual(self.df.index.names, r1.index.names)
        self.assertEqual(self.df.index.names, r2.index.names)


class TestTotalsAdd_DataFrameCategorical(unittest.TestCase):
    def setUp(self):
        self.totals_name = flatbread.agg.get_value('totals_name')
        df = pd._testing.makeDataFrame().head(5)
        df.columns = pd.Categorical(df.columns)
        df.index = pd.Categorical(df.index)
        self.df = df

    def test_add_column_total_to_rows(self):
        s = flatbread.totals.add(self.df, axis=0).loc[self.totals_name]
        self.assertTrue(s.equals(self.df.sum()))

    def test_add_row_total_to_cols(self):
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

    def test_add_column_total_to_rows(self):
        s = flatbread.totals.add(self.df, axis=0).iloc[-1]
        self.assertTrue(s.equals(self.df.sum()))

    def test_add_row_total_to_cols(self):
        s = flatbread.totals.add(self.df, axis=1).iloc[:, -1]
        self.assertTrue(s.equals(self.df.sum(axis=1)))

    def test_add_both(self):
        v = flatbread.totals.add(self.df, axis=2).iloc[-1, -1]
        self.assertTrue(v == self.df.sum().sum())

    def test_add_rows_within(self):
        left = (
            flatbread.totals.add(self.df, level=-1)
            .xs(flatbread.agg.get_value('subtotals_name'), level=-1)
            .values
        )
        right = self.df.groupby(level=-2).sum().values
        comparison = (left == right).all()
        self.assertTrue(comparison)

    def test_add_cols_within(self):
        left = (
            flatbread.totals.add(self.df, axis=1, level=1)
            .xs(flatbread.agg.get_value('subtotals_name'), axis=1, level=1)
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

    def test_preserve_axis_names(self):
        r1 = flatbread.totals.add(self.df)
        r2 = flatbread.totals.add(self.df, axis=1)
        r3 = flatbread.totals.add(self.df, level=1)
        r4 = flatbread.totals.add(self.df, axis=1, level=1)
        self.assertEqual(self.df.index.names, r1.index.names)
        self.assertEqual(self.df.index.names, r2.index.names)
        self.assertEqual(self.df.index.names, r3.index.names)
        self.assertEqual(self.df.index.names, r4.index.names)


if __name__ == "__main__":
    unittest.main()
