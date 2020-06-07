import flatbread.utils.log as log
from flatbread.core import copy


@copy
@log.entry
def columns(df, columns):
    "Select `columns` from `df`."

    return df[columns]


@copy
@log.entry
def rows(df, criteria, **kwargs):
    "Select rows meeting `criteria` from `df`."

    return df.query(criteria, **kwargs)


@copy
@log.entry
def aggfilter(df, aggfunc, criteria):
    "Select rows where `aggfunc` row aggregate meets `criteria`."

    evaluator = df.agg(aggfunc, axis=1)
    evaluator.name = aggfunc
    evaluator = evaluator.to_frame().eval(aggfunc + criteria)
    return df[evaluator]
