import unittest
from random import randint

import pandas as pd

import flatbread


class TestPercsTransform_DataFrameSimple(unittest.TestCase):
    def setUp(self):
        self.totals_name = flatbread.agg.get_value('totals_name')
        self.label_abs = flatbread.agg.get_value('label_abs')
        self.ndigits = flatbread.agg.get_value('ndigits')
        self.df = pd._testing.makeCustomDataframe(
            nrows=5,
            ncols=4,
            data_gen_f=lambda r,c:randint(1,100),
        )

    def test_value_percs_of_column_total(self):
        result = self.df.pipe(flatbread.percs.transform)
        test_value = result.iloc[0, 0]
        cell = self.df.iloc[0, 0]
        total = self.df.iloc[:, 0].sum()
        calc_perc = lambda a, b: round((a / b) * 100, self.ndigits)
        percentage = calc_perc(cell, total)
        self.assertEqual(test_value, percentage)

    def test_percs_of_column_add_to_100(self):
        result = self.df.pipe(flatbread.percs.transform)
        percs = result.iloc[:-1].sum().round(self.ndigits)
        totals = result.iloc[-1]
        self.assertTrue(percs.equals(totals))

    def test_percs_of_rows_add_to_100(self):
        result = self.df.pipe(flatbread.percs.transform, axis=1)
        percs = result.iloc[:, :-1].sum(axis=1).round(self.ndigits)
        totals = result.iloc[:, -1]
        self.assertTrue(percs.equals(totals))

    def test_original_data_after_adding_percentages(self):
        result = self.df.pipe(flatbread.percs.add, drop_totals=True)
        data = result.xs(self.label_abs, axis=1, level=-1)
        self.assertTrue(self.df.equals(data))
