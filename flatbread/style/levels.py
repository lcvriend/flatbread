import flatbread.config as config
import flatbread.style._helpers as helpers


@config.load_settings(['general', 'style', 'aggregation'])
@helpers.dicts_to_tuples
def add_level_dividers(
    df,
    uuid,
    *,
    level_row_border = None,
    level_col_border = None,
    totals_name = None,
    use_is_selector = None,
    **kwargs
):
    """
    Add borders between levels.

    Arguments
    ---------
    level_row_border : dict or list of tuples, optional
        Style for the border between two row levels.
    level_col_border : dict or list of tuples, optional
        Style for the border between two column levels.
    totals_name : scalar
        Name for the totals row/column.
    use_is_selector : bool, default False
        Use the ``:is()`` selector. Makes the resulting css cleaner. Not yet
        supported everywhere.
    """
    has_lvls = lambda idx: idx.nlevels > 1
    make_rows = _row_level_div_with_is if use_is_selector else _row_level_div
    make_cols = _col_level_div_with_is if use_is_selector else _col_level_div
    rows = make_rows(df, level_row_border, uuid) if has_lvls(df.index) else []
    cols = make_cols(df, level_col_border, uuid) if has_lvls(df.columns) else []
    return rows + cols


def _row_level_div(df, style, uuid):
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
            {"selector": row0, "props": style},
            {"selector": rown, "props": style},
        ]

    return [
        rule for level in range(ndivs)
        for rule in create_style_rules_rows(level)
        if rule is not None
    ]


def _row_level_div_with_is(df, style, *args):
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
        return [{"selector": selector, "props": style}]
    return [
        rule for level in range(ndivs)
        for rule in create_style_rules_rows(level)
        if rule is not None
    ]


def _col_level_div(df, style, uuid):
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


def _col_level_div_with_is(df, style, *args):
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
