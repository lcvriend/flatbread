import flatbread.utils.log as log
from flatbread.core import copy


@log.entry
def csv(path, **kwargs):
    "Load csv from `path`."

    return pd.read_csv(path, **kwargs)


@log.entry
def excel(path, **kwargs):
    "Load excel from `path`."

    return pd.read_excel(path, **kwargs)


@log.entry
def pickle(path):
    "Load pickle from `path`."

    return pd.read_pickle(path)


@copy
@log.entry
def merge(df1, df2, how='left', **kwargs):
    "Perform merge of type `how` on `df1` with `df2`."

    return df1.merge(df2, how=how, **kwargs)


@copy
@log.entry
def join(df1, df2, how='left', **kwargs):
    "Perform join on index of type `how` on `df1` with `df2`."

    return df1.join(df2, how=how, **kwargs)
