import unittest

import pandas as pd

import pita


class TestAssign_DataFrameSimple(unittest.TestCase):
    def setUp(self):
        self.df = pd._testing.makeDataFrame().head(5)
        self.df['E'] = range(5)

    def test_assign_scalar_criteria(self):
        x = 3
        y = 7
        s = pita.assign.values(
            self.df,
            values=y,
            column='E',
            criteria='E == @x')
        self.assertTrue(s.iloc[3].loc['E'], y)
