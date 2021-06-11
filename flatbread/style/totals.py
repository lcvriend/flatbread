import flatbread.config as c
import flatbread.utils as u
import flatbread.style._helpers as h
import flatbread.style.generic as g


@c.load_settings(['general', 'style', 'aggregation'])
@h.dicts_to_tuples
def add_totals_style(
    df,
    uuid,
    *,
    total_data_cell_style=None,
    total_header_cell_style=None,
    total_row_border=None,
    total_col_border=None,
    totals_name=None,
    use_is_selector=None,
    **kwargs
):
    total_header_cell_style = u.listify(total_header_cell_style)
    total_data_cell_style = u.listify(total_data_cell_style)
    total_row_border = u.listify(total_row_border)
    total_col_border = u.listify(total_col_border)

    make_rows = g._aggfunc_rows_with_is if use_is_selector else g._aggfunc_rows
    make_cols = g._aggfunc_cols_with_is if use_is_selector else g._aggfunc_cols

    rows = make_rows(
        df,
        total_data_cell_style,
        total_header_cell_style,
        total_row_border,
        totals_name,
        uuid,
        level=0,
    )
    cols = make_cols(
        df,
        total_data_cell_style,
        total_header_cell_style,
        total_col_border,
        totals_name,
        uuid,
        level=0,
    )
    return rows + cols


# def _row_level_dividers(df, level_row_border, totals_name):
#     """
#     Check for totals_name in keys of regular index, if found then add styling
#     to last row of the table body.
#     """
#     if totals_name in df.index:
#         return [{
#             "selector": "tbody tr:last-child", "props": level_row_border}]
#     else:
#         return []


# def _col_level_dividers(df, style, totals_name):
#     """
#     Check for totals_name in keys of regular column index, if found then add
#     styling to last column of the table body.
#     """
#     if totals_name in df.columns:
#         return [
#             {"selector": "td:last-child", "props": style},
#             {"selector": "thead th:last-child", "props": style},
#         ]
#     else:
#         return []
