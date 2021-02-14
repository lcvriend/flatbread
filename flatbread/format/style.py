import re
import flatbread.config as config
from functools import wraps
from flatbread.config import CONFIG


def dicts_to_tuples(func):
    """Convert key-word arguments containing a dict into a list of key-value tuples. Used for converting the styling stored in the json into the format
    that pandas wants it."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        for k1,v1 in kwargs.items():
            if isinstance(v1, dict):
                kwargs[k1] = [(k2,v2) for k2,v2 in v1.items()]
        return func(*args, **kwargs)
    return wrapper


@config.load_settings('style')
@dicts_to_tuples
def add_table_style(
    *,
    table_border_top = None,
    table_border_bottom = None,
    header_border_bottom = None,
    row_header_border = None,
    style_table = None,
    style_col_header = None,
    style_row_header = None,
    style_data = None,
    **kwargs
):
    return [
        # table
        {"selector": '', "props": style_table},
        {"selector": "thead tr:first-child", "props": table_border_top},
        {"selector": "tbody tr:last-child", "props": table_border_bottom},

        # header
        {"selector": "thead tr:last-child", "props": header_border_bottom},

        # columns
        {"selector": "thead th", "props": style_col_header},

        # index
        {"selector": "tbody th", "props": style_row_header},
        {"selector": "tbody tr th:last-of-type", "props": row_header_border},

        # data
        {"selector": "tbody td", "props": style_data},
    ]


@config.load_settings(['style', 'aggregation'])
@dicts_to_tuples
def add_level_dividers(
    df,
    uuid,
    *,
    row_border_levels = None,
    col_border_levels = None,
    totals_name = None,
    **kwargs
):
    if df.index.nlevels == 1:
        rows = _row_level_dividers(df, row_border_levels, totals_name)
    else:
        rows = _row_level_dividers_mi(df, uuid, row_border_levels)

    if df.columns.nlevels == 1:
        cols = _col_level_dividers(df, col_border_levels, totals_name)
    else:
        cols = _col_level_dividers_mi(df, uuid, col_border_levels)
    return rows + cols


def _row_level_dividers(df, row_border_levels, totals_name):
    """Check for totals_name in keys of regular index, if found then add styling
    to last row of the table body."""

    if totals_name in df.index:
        return [{"selector": "tbody tr:last-child", "props": row_border_levels}]
    else:
        return []


def _row_level_dividers_mi(df, uuid, row_border_levels):
    """Add styling to th and td for each row level in a multiindex, excluding
    the smallest level."""

    add_uuid = lambda x,uuid: uuid + x
    uuid = f"#T_{uuid}"
    nlevels = df.index.nlevels
    ndivs = nlevels - 1

    def create_style_rules_rows(level):
        row0 = f"th.row_heading.level{level}"
        rown = (
            f"th.row_heading.level{level}~th,"
            f"{uuid} th.row_heading.level{level}~td")
        return [
            {"selector": row0, "props": row_border_levels},
            {"selector": rown, "props": row_border_levels},
        ]

    return [
        rule for level in range(ndivs)
        for rule in create_style_rules_rows(level)
        if rule is not None
    ]


def _col_level_dividers(df, style, totals_name):
    """Check for totals_name in keys of regular column index, if found then add
    styling to last column of the table body."""

    if totals_name in df.columns:
        return [
            {"selector": "td:last-child", "props": style},
            {"selector": "thead th:last-child", "props": style},
        ]
    else:
        return []


def _col_level_dividers_mi(df, uuid, style):
    """Add styling to th, .blank and td for each col level in a multiindex,
    excluding the smallest level."""

    add_uuid = lambda x,uuid: uuid + x
    uuid = f"#T_{uuid} "

    def create_rules_for_thead(level, from_level):
        codes = [col[0:from_level + 1] for col in df.columns]
        prev = codes[0]
        selectors = list()
        for colnum, code in enumerate(codes):
            if code != prev:
                selector = f"th.level{level}.col{colnum}"
                selectors.append(add_uuid(selector, uuid))
            prev = code
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    def create_rules_for_blanks(from_level):
        offset = len(df.index.names) + 1
        codes = [col[0:from_level + 1] for col in df.columns]
        prev = codes[0]
        selectors = list()
        for colnum, code in enumerate(codes):
            if code != prev:
                selector = f"tr .blank:nth-child({colnum + offset})"
                selectors.append(add_uuid(selector, uuid))
            prev = code
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    def create_rules_for_tbody(from_level):
        codes = [col[0:from_level + 1] for col in df.columns]
        prev = codes[0]
        selectors = list()
        for colnum, code in enumerate(codes):
            if code != prev:
                selector = f"td.col{colnum}"
                selectors.append(add_uuid(selector, uuid))
            prev = code
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    nlevels = df.columns.nlevels
    ndivs = list()
    sticky = None
    for i in range(nlevels):
        if i < nlevels - 1:
            ndivs.append((i, i))
            sticky = i
        else:
            ndivs.append((i, sticky))

    dividers_thead = [
        rule for level in ndivs
        for rule in create_rules_for_thead(*level)
    ]
    dividers_blanks = create_rules_for_blanks(ndivs[-1][1])
    dividers_tbody = create_rules_for_tbody(ndivs[-1][1])
    return dividers_thead + dividers_tbody + dividers_blanks


@config.load_settings(['style', 'aggregation'])
@dicts_to_tuples
def add_subtotals_style(
    df,
    uuid,
    *,
    style_data_subtotal=None,
    style_header_subtotal=None,
    row_border_subtotal=None,
    col_border_subtotal=None,
    subtotals_name=None,
    **kwargs
):
    rows = _subtotal_rows(
        df,
        uuid,
        style_data_subtotal,
        style_header_subtotal,
        row_border_subtotal,
        subtotals_name,
    )
    cols = _subtotal_cols(
        df,
        uuid,
        style_data_subtotal,
        style_header_subtotal,
        col_border_subtotal,
        subtotals_name,
    )
    return rows + cols


def _subtotal_rows(
    df,
    uuid,
    style_data_subtotal,
    style_header_subtotal,
    row_border_subtotal,
    subtotals_name,
):
    add_uuid = lambda x,uuid: uuid + x
    uuid = f"#T_{uuid} "
    rows = [i for i, key in enumerate(df.index) if subtotals_name in key]

    def create_rules_for_data(rows):
        style = style_data_subtotal + row_border_subtotal
        selectors = list()
        for row in rows:
            for col in range(df.shape[1]):
                selector = f"td.row{row}.col{col}"
                selectors.append(add_uuid(selector, uuid))
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    def create_rules_for_index(rows):
        style = style_header_subtotal + row_border_subtotal
        selectors = list()
        for row in rows:
            start = df.index[row].index(subtotals_name)
            for level in range(start, df.index.nlevels):
                selector = f"th.level{level}.row{row}"
                selectors.append(add_uuid(selector, uuid))
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    data = create_rules_for_data(rows) if rows else []
    index = create_rules_for_index(rows) if rows else []
    return data + index


def _subtotal_cols(
    df,
    uuid,
    style_data_subtotal,
    style_header_subtotal,
    col_border_subtotal,
    subtotals_name,
):
    add_uuid = lambda x,uuid: uuid + x
    uuid = f"#T_{uuid} "
    cols = [i for i, key in enumerate(df.columns) if subtotals_name in key]

    def create_rules_for_data(cols):
        style = style_data_subtotal + col_border_subtotal
        selectors = list()
        for col in cols:
            for row in range(df.shape[0]):
                selector = f"td.row{row}.col{col}"
                selectors.append(add_uuid(selector, uuid))
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    def create_rules_for_index(cols):
        style = style_header_subtotal + col_border_subtotal
        selectors = list()
        for col in cols:
            start = df.columns[col].index(subtotals_name)
            for level in range(start, df.columns.nlevels):
                selector = f"th.level{level}.col{col}"
                selectors.append(add_uuid(selector, uuid))
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    def create_rules_for_blanks(cols):
        style = style_header_subtotal + col_border_subtotal
        offset = len(df.index.names) + 1
        selectors = list()
        for col in cols:
            selector = f"tr .blank:nth-child({col + offset})"
            selectors.append(add_uuid(selector, uuid))
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    data = create_rules_for_data(cols) if cols else []
    index = create_rules_for_index(cols) if cols else []
    blanks = create_rules_for_blanks(cols) if cols else []
    return data + index + blanks


@dicts_to_tuples
def get_style(df, uuid, **kwargs):
    table = add_table_style(**kwargs)
    levels = add_level_dividers(df, uuid, **kwargs)
    subtotals = add_subtotals_style(df, uuid, **kwargs)
    return table + levels + subtotals


def get_inline_css_from_html(html):
    regex = '<style.*>([\n\s\w\W]*)</style>'
    match = re.search(regex, html).group(1)
    return match.replace('}', '}\n')
