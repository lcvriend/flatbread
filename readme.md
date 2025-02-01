# Flatbread

Flatbread is a Python library that extends pandas with tabulation features. It makes it easy to create and display summary tables with totals, subtotals, percentages, and aggregations.

Flatbread can be accessed in `DataFrames` and `Series` using the `pita` accessor.

## Key Features

- Add row and column totals/subtotals to DataFrames and Series
- Calculate and format percentages with proper rounding
- Preserve data types and index structures
- Table display in Jupyter notebooks

## Quick Example

```python
import pandas as pd
import flatbread

df = pd.DataFrame(...)

# Add totals and percentages
result = (
    df
    .pita.add_totals()           # Add grand totals
    .pita.add_subtotals(level=0) # Add subtotals by first index level
    .pita.add_percentages()      # Add percentage columns
)

# Display with interactive viewer
result.pita.configure_display(
    locale="en-US",
    show_hover=True,
    section_levels=1
)
```

## Installation

```bash
pip install flatbread
```

## Main Features

- **Totals**: Add row/column totals with `add_totals()` 
- **Subtotals**: Add subtotals by index level with `add_subtotals()`
- **Percentages**: Add percentage calculations with `add_percentages()`
- **Aggregation**: Custom aggregations with `add_agg()`
- **Display**: Table viewer with rich formatting options
