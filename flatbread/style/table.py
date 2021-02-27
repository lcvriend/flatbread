import flatbread.config as config
import flatbread.style._helpers as helpers


@config.load_settings('style')
@helpers.dicts_to_tuples
def add_table_style(
    *,
    table_border_top = None,
    table_border_bottom = None,
    header_border_bottom = None,
    row_header_border = None,
    style_table = None,
    style_caption = None,
    style_col_header = None,
    style_row_header = None,
    style_data = None,
    style_data_row = None,
    style_data_row_hover = None,
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
    header_border_bottom : dict or list of tuples, optional
        Style for the bottom border of the header.
    row_header_border : dict or list of tuples, optional
        Style for the border of the table row index.
    style_table : dict or list of tuples, optional
        Style applied to the table elemment.
    style_caption : dict or list of tuples, optional
        Style applied to the caption element.
    style_col_header : dict or list of tuples, optional
        Style applied to the column header.
    style_row_header : dict or list of tuples, optional
        Style applied to the row header.
    style_data : dict or list of tuples, optional
        Style applied to the data cells.
    style_data_row : dict or list of tuples, optional
        Style applied to the data rows.
    style_data_row_hover : dict or list of tuples, optional
        Style applied on hover over data rows.

    Returns
    -------
    List of dicts
    """
    styles = [
        # table
        {"selector": "", "props": style_table},
        {"selector": "thead tr:first-child", "props": table_border_top},
        {"selector": "tbody tr:last-child", "props": table_border_bottom},

        #caption
        {"selector": "caption", "props": style_caption},

        # header
        {"selector": "thead tr:last-child", "props": header_border_bottom},

        # columns
        {"selector": "thead th", "props": style_col_header},

        # index
        {"selector": "tbody th", "props": style_row_header},
        {"selector": "tbody tr th:last-of-type", "props": row_header_border},

        # data
        {"selector": "tbody td", "props": style_data},
        {"selector": "tbody tr", "props": style_data_row},
        {"selector": "tbody tr:hover", "props": style_data_row_hover},
    ]
    return [style for style in styles if style['props'] is not None]


@config.load_settings('style')
@helpers.dicts_to_tuples
def add_flatbread_style(
    uuid,
    *,
    style_title=None,
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
    style_title : dict or list of tuples, optional
        Style applied to the title of the table (if one is added).

    Returns
    -------
    List of dicts
    """
    args = locals()
    todo = list()

    selectors = dict(
        style_title = "h3",
    )

    for k,v in args.items():
        if k == 'uuid' or k == 'kwargs' or not v:
            continue
        todo.append(dict(selector=selectors[k], props=v))
    return todo
