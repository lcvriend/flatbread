import flatbread.config as config
import flatbread.style._helpers as helpers


@config.load_settings(['style', 'aggregation'])
@helpers.dicts_to_tuples
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
    test = lambda x,lbl: lbl in x if isinstance(x, tuple) else lbl == x
    rows = [i for i, key in enumerate(df.index) if test(key, subtotals_name)]

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
    test = lambda x,lbl: lbl in x if isinstance(x, tuple) else lbl == x
    cols = [i for i, key in enumerate(df.columns) if test(key, subtotals_name)]

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
