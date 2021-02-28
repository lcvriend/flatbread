"""
Provide access to some of pandas' data loaders.
"""

import pandas as pd # type: ignore

import flatbread.utils as utils
import flatbread.utils.log as log


@log.entry
def csv(path, **kwargs) -> pd.DataFrame:
    "Load csv from `path`."
    return pd.read_csv(path, **kwargs)


@log.entry
def excel(path, **kwargs) -> pd.DataFrame:
    "Load excel from `path`."
    return pd.read_excel(path, **kwargs)


@log.entry
def pickle(path) -> pd.DataFrame:
    "Load pickle from `path`."
    return pd.read_pickle(path)


@utils.copy
@log.entry
def merge(df1, df2, how='left', **kwargs) -> pd.DataFrame:
    "Perform merge of type `how` on `df1` with `df2`."
    return df1.merge(df2, how=how, **kwargs)


@utils.copy
@log.entry
def join(df1, df2, how='left', **kwargs) -> pd.DataFrame:
    "Perform join on index of type `how` on `df1` with `df2`."
    return df1.join(df2, how=how, **kwargs)
