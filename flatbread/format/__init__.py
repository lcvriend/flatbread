from flatbread.config import load_settings


FORMAT_SETTINGS = {'format': ['na_rep']}


@load_settings(FORMAT_SETTINGS)
def format(df, na_rep=None):
    return df.style.format(lambda x: f'{x:n}', na_rep=na_rep)
