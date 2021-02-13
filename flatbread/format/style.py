import re
import flatbread.config as config
from flatbread.config import CONFIG

@config.load_settings('style')
def table_style(
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
def level_dividers(
    df,
    row_border_levels = None,
    col_border_levels = None,
    totals_name = None,
    **kwargs
):
    if df.index.nlevels == 1:
        rows = _row_level_dividers(df, row_border_levels, totals_name)
    else:
        rows = _row_level_dividers_mi(df, row_border_levels)

    if df.columns.nlevels == 1:
        cols = _col_level_dividers(df, col_border_levels, totals_name)
    else:
        cols = _col_level_dividers_mi(df, col_border_levels)
    return rows + cols


def _row_level_dividers(df, style, totals_name):
    if totals_name in df.index:
        return [{"selector": "tbody tr:last-child", "props": style}]
    else:
        return []


def _row_level_dividers_mi(
    df,
    row_border_levels,
):
    nlevels = df.index.nlevels
    ndivs = nlevels - 1

    def create_style_rules_rows(level):
        row0 = f"th.row_heading.level{level}"
        rown = f"th.row_heading.level{level}~th, th.row_heading.level{level}~td"
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
    if totals_name in df.columns:
        return [
            {"selector": "td:last-child", "props": style},
            {"selector": "thead th:last-child", "props": style}
        ]
    else:
        return []


def _col_level_dividers_mi(df, style):

    def create_rules_for_thead(level, from_level):
        codes = [col[0:from_level + 1] for col in df.columns]
        prev = codes[0]
        selectors = list()
        for colnum, code in enumerate(codes):
            if code != prev:
                selectors.append(f"th.level{level}.col{colnum}")
            prev = code
        return [{"selector": ', '.join(selectors), "props": style}]

    def create_rules_for_blanks(from_level):
        offset = len(df.index.names) + 1
        codes = [col[0:from_level + 1] for col in df.columns]
        prev = codes[0]
        selectors = list()
        for colnum, code in enumerate(codes):
            if code != prev:
                selectors.append(f"tr .blank:nth-child({colnum + offset})")
            prev = code
        return [{"selector": ', '.join(selectors), "props": style}]

    def create_rules_for_tbody(from_level):
        codes = [col[0:from_level + 1] for col in df.columns]
        prev = codes[0]
        selectors = list()
        for colnum, code in enumerate(codes):
            if code != prev:
                selectors.append(f"td.col{colnum}")
            prev = code
        return [{"selector": ', '.join(selectors), "props": style}]

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


def get_style(df):
    return table_style() + level_dividers(df)


def get_inline_css_from_html(html):
    regex = '<style.*>([\n\s\w\W]*)</style>'
    html = piv.style().render()
    match = re.search(regex, html).group(1)
    return match.replace('}', '}\n')
