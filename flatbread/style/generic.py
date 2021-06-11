from flatbread.utils import get_label_indeces


def _aggfunc_rows(
    df,
    style_data_aggfunc,
    style_header_aggfunc,
    row_border_aggfunc,
    aggfunc,
    uuid,
    level = None,
):
    add_uuid = lambda x,uuid: uuid + x
    uuid = f"#T_{uuid} "
    rows = get_label_indeces(df.index, aggfunc, level)

    def create_rules_for_data(rows):
        style_elements = style_data_aggfunc + row_border_aggfunc
        style = [i for i in style_elements if i]
        selectors = list()
        for row in rows:
            for col in range(df.shape[1]):
                # :not(#\9) is necessary to increase specificity by 1
                # if this is not added and the aggfunc is added to
                # not the lowest available level, then the regular
                # level border will override the aggfunc styling
                selector = f"td.row{row}.col{col}:not(#\9)"
                selectors.append(add_uuid(selector, uuid))
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    def create_rules_for_index(rows):
        style_elements = style_header_aggfunc + row_border_aggfunc
        style = [i for i in style_elements if i]
        selectors = list()
        for row in rows:
            start = df.index[row].index(aggfunc)
            for level in range(start, df.index.nlevels):
                selector = f"th.level{level}.row{row}:not(#\9)"
                selectors.append(add_uuid(selector, uuid))
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    data = create_rules_for_data(rows) if rows else []
    index = create_rules_for_index(rows) if rows else []
    return data + index


def _aggfunc_rows_with_is(
    df,
    style_data_aggfunc,
    style_header_aggfunc,
    row_border_aggfunc,
    aggfunc,
    *args, # added in order to be able to ignore uuid
    level = None,
):
    rows = get_label_indeces(df.index, aggfunc, level)

    def create_rules_for_data(rows):
        style_elements = style_data_aggfunc + row_border_aggfunc
        style = [i for i in style_elements if i]
        selectors = list()
        for row in rows:
            for col in range(df.shape[1]):
                # :not(#\9) is necessary to increase specificity by 1
                # if this is not added and the aggfunc is added to
                # not the lowest available level, then the regular
                # level border will override the aggfunc styling
                selector = f"td.row{row}.col{col}:not(#\9)"
                selectors.append(selector)
        combined_selectors = f":is({', '.join(s for s in selectors)})"
        return [{"selector": combined_selectors, "props": style}]

    def create_rules_for_index(rows):
        style_elements = style_header_aggfunc + row_border_aggfunc
        style = [i for i in style_elements if i]
        selectors = list()
        for row in rows:
            start = df.index[row].index(aggfunc)
            for level in range(start, df.index.nlevels):
                selector = f"th.level{level}.row{row}:not(#\9)"
                selectors.append(selector)
        combined_selectors = f":is({', '.join(s for s in selectors)})"
        return [{"selector": combined_selectors, "props": style}]

    data = create_rules_for_data(rows) if rows else []
    index = create_rules_for_index(rows) if rows else []
    return data + index


def _aggfunc_cols(
    df,
    style_data_aggfunc,
    style_header_aggfunc,
    col_border_aggfunc,
    aggfunc,
    uuid,
    level = None,
):
    add_uuid = lambda x, uuid: uuid + x
    uuid = f"#T_{uuid} "
    cols = get_label_indeces(df.columns, aggfunc, level)

    def create_rules_for_data(cols):
        style_elements = style_data_aggfunc + col_border_aggfunc
        style = [i for i in style_elements if i]
        selectors = list()
        for col in cols:
            for row in range(df.shape[0]):
                selector = f"td.row{row}.col{col}"
                selectors.append(add_uuid(selector, uuid))
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    def create_rules_for_index(cols):
        style_elements = style_header_aggfunc + col_border_aggfunc
        style = [i for i in style_elements if i]
        selectors = list()
        for col in cols:
            start = df.columns[col].index(aggfunc)
            for level in range(start, df.columns.nlevels):
                selector = f"th.level{level}.col{col}"
                selectors.append(add_uuid(selector, uuid))
        return [{"selector": ', '.join(selectors)[len(uuid):], "props": style}]

    def create_rules_for_blanks(cols):
        style = style_header_aggfunc + col_border_aggfunc
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


def _aggfunc_cols_with_is(
    df,
    style_data_aggfunc,
    style_header_aggfunc,
    col_border_aggfunc,
    aggfunc,
    *args, # added in order to be able to ignore uuid
    level = None,
):
    cols = get_label_indeces(df.columns, aggfunc, level)

    def create_rules_for_data(cols):
        style_elements = style_data_aggfunc + col_border_aggfunc
        style = [i for i in style_elements if i]
        selectors = list()
        for col in cols:
            for row in range(df.shape[0]):
                selector = f"td.row{row}.col{col}"
                selectors.append(selector)
        combined_selectors = f":is({', '.join(s for s in selectors)})"
        return [{"selector": combined_selectors, "props": style}]

    def create_rules_for_index(cols):
        style_elements = style_header_aggfunc + col_border_aggfunc
        style = [i for i in style_elements if i]
        selectors = list()
        for col in cols:
            start = df.columns[col].index(aggfunc)
            for level in range(start, df.columns.nlevels):
                selector = f"th.level{level}.col{col}"
                selectors.append(selector)
        combined_selectors = f":is({', '.join(s for s in selectors)})"
        return [{"selector": combined_selectors, "props": style}]

    def create_rules_for_blanks(cols):
        style = style_header_aggfunc + col_border_aggfunc
        offset = len(df.index.names) + 1
        selectors = list()
        for col in cols:
            selector = f"tr .blank:nth-child({col + offset})"
            selectors.append(selector)
        combined_selectors = f":is({', '.join(s for s in selectors)})"
        return [{"selector": combined_selectors, "props": style}]

    data = create_rules_for_data(cols) if cols else []
    index = create_rules_for_index(cols) if cols else []
    blanks = create_rules_for_blanks(cols) if cols else []
    return data + index + blanks
