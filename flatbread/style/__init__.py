"""
Styling for flatbread's pivot tables. Contains
:py:class:`flatbread.style.FlatbreadStyler` which subclasses :py:class:`pandas.io.formats.style.Styler`.
Modules contain functions for building up the styling for flatbread's tables:

:py:mod:`flatbread.style.levels` :
    Add borders between groups and total rows/columns.
:py:mod:`flatbread.style.subtotals` :
    Add styling for subtotal rows/columns.
:py:mod:`flatbread.style.table` :
    Add styling for table and table container.
"""


from flatbread.style.styler import FlatbreadStyler
