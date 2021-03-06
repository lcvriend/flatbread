import flatbread.config as config
import flatbread.style._helpers as helpers


@config.load_settings(['general', 'style', 'aggregation'])
@helpers.dicts_to_tuples
def add_level_dividers(
    df,
    uuid,
    *,
    row_border_levels = None,
    col_border_levels = None,
    totals_name = None,
    use_is_selector = None,
    **kwargs
):
    """
    Add borders between levels.

    Arguments
    ---------
    row_border_levels : dict or list of tuples, optional
        Style for the border between two row levels.
    col_border_levels : dict or list of tuples, optional
        Style for the border between two column levels.
    totals_name : scalar
        Name for the totals row/column.
    use_is_selector : bool, default False
        Use the ``:is()`` selector. Makes the resulting css cleaner. Not yet
        supported everywhere.
    """
    if df.index.nlevels == 1:
        rows = _row_level_dividers(df, row_border_levels, totals_name)
    else:
        if use_is_selector:
            rows = _row_level_dividers_mi_with_is(df, row_border_levels)
        else:
            rows = _row_level_dividers_mi(df, uuid, row_border_levels)

    if df.columns.nlevels == 1:
        cols = _col_level_dividers(df, col_border_levels, totals_name)
    else:
        if use_is_selector:
            cols = _col_level_dividers_mi_with_is(df, col_border_levels)
        else:
            cols = _col_level_dividers_mi(df, uuid, col_border_levels)
    return rows + cols


def _row_level_dividers(df, row_border_levels, totals_name):
    """
    Check for totals_name in keys of regular index, if found then add styling
    to last row of the table body.
    """
    if totals_name in df.index:
        return [{
            "selector": "tbody tr:last-child", "props": row_border_levels}]
    else:
        return []


def _row_level_dividers_mi(df, uuid, row_border_levels):
    """
    Add styling to th and td for each row level in a multiindex, excluding
    the smallest level.
    """
    uuid = f"#T_{uuid}"
    ndivs = df.index.nlevels - 1

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


def _row_level_dividers_mi_with_is(df, row_border_levels):
    """
    Add styling to th and td for each row level in a multiindex, excluding
    the smallest level.
    """
    ndivs = df.index.nlevels - 1
    def create_style_rules_rows(level):
        selectors = [
            f"th.row_heading.level{level}",
            f"th.row_heading.level{level}~th",
            f"th.row_heading.level{level}~td",
        ]
        selector = f":is({', '.join(s for s in selectors)})"
        return [{"selector": selector, "props": row_border_levels}]
    return [
        rule for level in range(ndivs)
        for rule in create_style_rules_rows(level)
        if rule is not None
    ]


def _col_level_dividers(df, style, totals_name):
    """
    Check for totals_name in keys of regular column index, if found then add
    styling to last column of the table body.
    """
    if totals_name in df.columns:
        return [
            {"selector": "td:last-child", "props": style},
            {"selector": "thead th:last-child", "props": style},
        ]
    else:
        return []


def _col_level_dividers_mi(df, uuid, style):
    """
    Add styling to th, .blank and td for each col level in a multiindex,
    excluding the smallest level.
    """

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


def _col_level_dividers_mi_with_is(df, style):
    """Add styling to th, .blank and td for each col level in a multiindex,
    excluding the smallest level."""

    def create_rules_for_thead(level, from_level):
        codes = [col[0:from_level + 1] for col in df.columns]
        prev = codes[0]
        selectors = list()
        for colnum, code in enumerate(codes):
            if code != prev:
                selectors.append(f"th.level{level}.col{colnum}")
            prev = code
        return [{"selector": f":is({', '.join(selectors)})", "props": style}]

    def create_rules_for_blanks(from_level):
        offset = len(df.index.names) + 1
        codes = [col[0:from_level + 1] for col in df.columns]
        prev = codes[0]
        selectors = list()
        for colnum, code in enumerate(codes):
            if code != prev:
                selectors.append(f"tr .blank:nth-child({colnum + offset})")
            prev = code
        return [{"selector": f":is({', '.join(selectors)})", "props": style}]

    def create_rules_for_tbody(from_level):
        codes = [col[0:from_level + 1] for col in df.columns]
        prev = codes[0]
        selectors = list()
        for colnum, code in enumerate(codes):
            if code != prev:
                selectors.append(f"td.col{colnum}")
            prev = code
        return [{"selector": f":is({', '.join(selectors)})", "props": style}]

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
