def formatter(df, nan=''):
    def format_int(x):
        if x != x:
            return nan
        return f'{x:,.0f}'.replace(',', '.')

    def format_float(x):
        if x != x:
            return nan
        x = list(f'{x:,.1f}'.replace(',', '.'))
        x[-2] = ','
        return ''.join(x)

    mapper = {
        pd.np.dtype('int64'): format_int,
        pd.np.dtype('int32'): format_int,
        pd.Int64Dtype(): format_int,
        pd.np.dtype('float64'): format_float,
    }

    df = df.copy()
    ops = {k:mapper[v] for k,v in df.dtypes.items() if v in mapper}
    for col, op in ops.items():
        df[col] = df[col].apply(op)
    return df
