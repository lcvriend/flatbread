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
    index_header_cell_style = None,
    data_cell_style = None,
    data_row_style = None,
    data_row_style_hover = None,
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
    index_header_cell_style : dict or list of tuples, optional
        Style applied to the row header.
    data_style : dict or list of tuples, optional
        Style applied to the data cells.
    data_row_style : dict or list of tuples, optional
        Style applied to the data rows.
    data_row_style_hover : dict or list of tuples, optional
        Style applied on hover over data rows.

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

        # index
        {"selector": "tbody th", "props": index_header_cell_style},
        {"selector": "tbody tr th:last-of-type", "props": index_data_border},

        # data
        {"selector": "tbody td", "props": data_cell_style},
        {"selector": "tbody tr", "props": data_row_style},
        {"selector": "tbody tr:hover", "props": data_row_style_hover},
    ]
    return [style for style in styles if style['props']]


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
