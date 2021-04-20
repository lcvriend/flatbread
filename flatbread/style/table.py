from pandas.api.types import (
    is_bool_dtype,
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_string_dtype,
)

import flatbread.config as config
import flatbread.style._helpers as helpers


@config.load_settings('style')
@helpers.dicts_to_tuples
def add_table_style(
    *,
    table_border_top = None,
    table_border_bottom = None,
    columns_data_border = None,
    index_data_border = None,
    table_style = None,
    caption_style = None,
    columns_header_cell_style = None,
    column_names_cell_style = None,
    index_names_cell_style = None,
    index_header_cell_style = None,
    data_cell_style = None,
    body_row_style = None,
    body_row_style_hover = None,
    body_row_style_odd = None,
    body_row_style_even = None,
    **kwargs
):
    """
    Create table styling as list of dicts of selector/properties.
    Styling applies to every table regardless of its contents.

    Styling defaults to what is set in config.

    Arguments
    ---------
    table_border_top : dict or list of tuples, optional
        Style for the top border of the table.
    table_border_bottom : dict or list of tuples, optional
        Style for the bottom border of the table.
    columns_data_border : dict or list of tuples, optional
        Style for the bottom border of the header.
    index_data_border : dict or list of tuples, optional
        Style for the border of the table row index.
    table_style : dict or list of tuples, optional
        Style applied to the table elemment.
    caption_style : dict or list of tuples, optional
        Style applied to the caption element.
    columns_header_cell_style : dict or list of tuples, optional
        Style applied to the column header.
    column_names_cell_style : dict or list of tuples, optional
        Style applied to names of index and columns.
    index_names_cell_style : dict or list of tuples, optional
        Style applied to names of index and columns.
    index_header_cell_style : dict or list of tuples, optional
        Style applied to the row header.
    data_style : dict or list of tuples, optional
        Style applied to the data cells.
    body_row_style : dict or list of tuples, optional
        Style applied to the body rows.
    body_row_style_hover : dict or list of tuples, optional
        Style applied on hover over body rows.
    body_row_style_odd : dict or list of tuples, optional
    body_row_style_even : dict or list of tuples, optional

    Returns
    -------
    List of dicts
    """
    styles = [
        # table
        {"selector": "", "props": table_style},
        {"selector": "thead tr:first-child", "props": table_border_top},
        {"selector": "tbody tr:last-child", "props": table_border_bottom},

        #caption
        {"selector": "caption", "props": caption_style},

        # header
        {"selector": "thead tr:last-child", "props": columns_data_border},

        # columns
        {"selector": "thead th", "props": columns_header_cell_style},
        {"selector": "th.index_name", "props": column_names_cell_style},
        {"selector": "tr:last-child th.index_name", "props": index_names_cell_style},

        # index
        {"selector": "tbody th", "props": index_header_cell_style},
        {"selector": "tbody tr th:last-of-type", "props": index_data_border},

        # rows
        {"selector": "tbody tr", "props": body_row_style},
        {"selector": "tbody tr:hover:not(#\9)", "props": body_row_style_hover},
        {"selector": "tbody tr:nth-of-type(odd)", "props": body_row_style_odd},
        {"selector": "tbody tr:nth-of-type(even)", "props": body_row_style_even},

        # data
        {"selector": "tbody td", "props": data_cell_style},
    ]
    return [style for style in styles if style['props']]


@config.load_settings('style')
@helpers.dicts_to_tuples
def add_column_styles(
    df,
    data_column_number = None,
    data_column_string = None,
    data_column_boolean = None,
    data_column_datetime = None,
    data_column_categorical = None,
    **kwargs,
):
    """
    TBD
    """
    tests = {
        is_bool_dtype: data_column_boolean,
        is_numeric_dtype: data_column_number,
        is_string_dtype: data_column_string,
        is_datetime64_any_dtype: data_column_datetime,
        is_categorical_dtype: data_column_categorical,
    }
    # ignore test if no style has been defined for it
    tests = {func:props for func, props in tests.items() if props}
    styles = {}
    for col in df.columns:
        for test, props in tests.items():
            if test(df[col]):
                styles[col] = [{'selector': 'td', 'props': props}]
                break
    return styles


@config.load_settings('style')
@helpers.dicts_to_tuples
def add_flatbread_style(
    uuid,
    *,
    title_style = None,
    **kwargs
):
    """
    Create styling for the flatbread container as list of dicts of
    selector/properties. Styling applies to every flatbread element regardless
    of its contents.

    Each table is wrapped in a flatbread ``div`` and may contain additional
    elements such as a title.

    Styling defaults to what is set in config.

    Arguments
    ---------
    title_style : dict or list of tuples, optional
        Style applied to the title of the table (if one is added).

    Returns
    -------
    List of dicts
    """
    args = locals()
    todo = list()

    selectors = dict(
        title_style = "h3",
    )

    for k,v in args.items():
        if k == 'uuid' or k == 'kwargs' or not v:
            continue
        todo.append(dict(selector=selectors[k], props=v))
    return todo
