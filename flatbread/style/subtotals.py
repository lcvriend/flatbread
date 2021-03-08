import flatbread.config as c
import flatbread.utils as u
import flatbread.style._helpers as h
import flatbread.style.generic as g


@c.load_settings(['general', 'style', 'aggregation'])
@h.dicts_to_tuples
def add_subtotals_style(
    df,
    uuid,
    *,
    subtotal_data_cell_style=None,
    subtotal_header_cell_style=None,
    subtotal_row_border=None,
    subtotal_col_border=None,
    subtotals_name=None,
    use_is_selector=None,
    **kwargs
):
    subtotal_header_cell_style = u.listify(subtotal_header_cell_style)
    subtotal_data_cell_style = u.listify(subtotal_data_cell_style)
    subtotal_row_border = u.listify(subtotal_row_border)
    subtotal_col_border = u.listify(subtotal_col_border)

    make_rows = g._aggfunc_rows_with_is if use_is_selector else g._aggfunc_rows
    make_cols = g._aggfunc_cols_with_is if use_is_selector else g._aggfunc_cols

    rows = make_rows(
        df,
        subtotal_data_cell_style,
        subtotal_header_cell_style,
        subtotal_row_border,
        subtotals_name,
        uuid,
    )
    cols = make_cols(
        df,
        subtotal_data_cell_style,
        subtotal_header_cell_style,
        subtotal_col_border,
        subtotals_name,
        uuid,
    )
    return rows + cols
