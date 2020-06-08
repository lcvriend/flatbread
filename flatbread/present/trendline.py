from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
from flatbread.core.axes.index import timeseries_offset
from flatbread.config import PATHS

today_as_string = str(datetime.now().date())


LAYOUT = dict(
    general = dict(
        grid=True,
    ),
    comparison = dict(
        alpha=0.5,
        linestyle='--',
    ),
    size = dict(
        width = 6,
        height = 4,
    ),
)


class TrendLine(object):
    """
    TrendLine
    =========
    Object for plotting data with a DatetimeIndex.
    Parameters can be set when initializing but also when plotting.
    Plot can display several trendlines by group.
    Plot can be split up into subplots (rows and/or columns).
    Use ordered categorical variables to control display order.

    Parameters
    ==========
    ts : DataFrame
        Timeseries consisting of a DataFrame with DateTimeIndex.
    start : str, optional
        Start date used for slicing the DateTimeIndex.
    end : str, optional
        End date used for slicing the DateTimeIndex.
    period : DateOffset, Timedelta or str, default 'd'
        The offset string or object representing target conversion.
        {'d', 'w', 'm', 'y'}
    kind : str, default 'line'
        The kind of plot to produce:
            'line' : line plot (default)
            'bar' : vertical bar plot
            'barh' : horizontal bar plot
            'area' : area plot
    stacked : bool, default True
        Stack plots on top of each other.
    cum : bool, default False
        Create a cumulative plot.
    grouper : str, optional
        Name of the column to group by.
    focus : optional
        Value within the group to focus on.
        'comparison'-styling will be applied to the other groups.
    rows : str, optional
        Name of the column for splitting the plots into rows.
    cols : str, optional
        Name of the column for splitting the plots into columns.
    filter : str, optional
        The query string to evaluate.
    xticklabels : list[str], optional
        List of string labels.
    width : int, optional
        Width in inches of the plot or subplot.
    height : int, optional
        Height in inches of the plot or subplot.
    """

    general = {}
    comparison = {}
    size = {}
    colors = [
        'tab:blue',
        'tab:orange',
        'tab:green',
        'tab:red',
        'tab:purple',
        'tab:brown',
        'tab:pink',
        'tab:gray',
        'tab:olive',
        'tab:cyan',
    ]


    def __init__(
        self,
        ts,
        start       = None,
        end         = None,
        xaxis       = None,
        period      = 'd',
        kind        = 'line',
        stacked     = False,
        cum         = False,
        grouper     = None,
        focus       = None,
        rows        = None,
        cols        = None,
        filter      = None,
        xticklabels = None,
        width       = None,
        height      = None,
        extension   = 'png',
    ):
        self.ts          = ts
        self.start       = start
        self.end         = end
        self.xaxis       = xaxis
        self.period      = period
        self.kind        = kind
        self.stacked     = stacked
        self.cum         = cum
        self.grouper     = grouper
        self.focus       = focus
        self.rows        = rows
        self.cols        = cols
        self.filter      = filter
        self.xticklabels = xticklabels
        self.width       = width or {**LAYOUT['size'], **self.size}['width']
        self.height      = height or {**LAYOUT['size'], **self.size}['height']
        self.extension   = extension


    @property
    def ts(self):
        "Timeseries after optional date range and filters have been applied."

        ts = self._ts.copy()
        if self.start is not None or self.end is not None:
            ts = ts.loc[self.start:self.end]
        if self.filter is not None:
            ts = ts.query(self.filter)
        return ts


    @ts.setter
    def ts(self, ts):
        self._ts = ts


    @property
    def figure(self):
        "Last plotted figure. Returns if None if nothing has been plotted yet."

        if hasattr(self, '_figure'):
            return self._figure
        return None


    @property
    def filename(self):
        def repr(attr, len=5):
            value = getattr(self, attr)
            if value is None:
                return None
            else:
                value = str(value).lower()
                return f"{attr[0]}[{value}]"
                # vowels = ['a', 'e', 'i', 'o', 'u', 'y']
                # value = ''.join([char for char in value if char not in vowels])
                # return f"{attr[0]}[{value[:len]:_<{len}}]"

        args = [
            today_as_string,
            'trend',
            self.xaxis or self.data.index.name,
            self.kind,
            'cum' if self.cum else 'abs',
            'stacked' if self.stacked else None,
            None if self.xaxis is not None else repr('period', len=1),
            repr('grouper'),
            repr('rows'),
            repr('cols'),
            repr('start', len=10),
            repr('end', len=10),
            f"[{self.filter.replace(' ', '_')}]" if self.filter is not None else None,
            self.extension,
        ]
        return '.'.join([arg for arg in args if arg is not None])


    def savefig(self, filename=None):
        "Save the figure as `extension`."

        if filename is None:
            PATHS.graphs.mkdir(parents=True, exist_ok=True)
            filename = PATHS.graphs / self.filename
        self.figure.savefig(filename)


    @property
    def data(self):
        "The aggregated data used for plotting."

        data = self.ts
        data['_unit'] = 1
        if self.xaxis is not None:
            return self.pivot(data)
        else:
            return self.resample(data)


    def pivot(self, data):
        groupers = [self.rows, self.cols, self.xaxis]
        index = [grouper for grouper in groupers if grouper is not None]
        if self.grouper is not None:
            data = data.pivot_table(
                index   = index,
                columns = self.grouper,
                values  = '_unit',
                aggfunc = 'count',
            )
        else:
            data = data.pivot_table(
                index   = index,
                aggfunc = 'size',
            )

        if self.cum:
            return data.cumsum()
        return data


    def resample(self, data):
        groupers = [self.grouper, self.rows, self.cols]
        groupby = [grouper for grouper in groupers if grouper is not None]
        if groupby:
            data = data.groupby(groupby, observed=True)

        data = (
            data
            .resample(self.period)
            ._unit
            .count()
            .unstack(0)
        )

        groupers = [self.rows, self.cols]
        groupby = [grouper for grouper in groupers if grouper is not None]
        if groupby:
            data = data.groupby(groupby).fillna(method='bfill')
            if self.cum:
                return data.groupby(groupby).cumsum()
            return data

        data = data.fillna(method='bfill')
        if self.cum:
            return data.cumsum()
        return data


    @property
    def groups(self):
        "Groups within the data."

        if self.grouper is None:
            return None
        return self.get_values(self.ts[self.grouper])


    @property
    def row_values(self):
        "Row values."

        if self.rows is None:
            return None
        return self.get_values(self.ts[self.rows])


    @property
    def col_values(self):
        "Column values."

        if self.cols is None:
            return None
        return self.get_values(self.ts[self.cols])


    @property
    def nrows(self):
        "Number of rows within the plot."

        if self.rows is None:
            return 1
        return len(self.row_values)


    @property
    def ncols(self):
        "Number of columns within the plot."

        if self.cols is None:
            return 1
        return len(self.col_values)


    @property
    def styling(self):
        "Color assignment per group."

        if self.groups is not None:
            colors = zip(self.groups, self.colors)
            return {group:color for group, color in colors}
        else:
            None


    @property
    def layout_general(self):
        return {**LAYOUT['general'], **self.general}


    @property
    def layout_comparison(self):
        return {**LAYOUT['comparison'], **self.comparison}


    def reset(self):
        "Reset parameters to their default."

        self.start       = None
        self.end         = None
        self.period      = 'd'
        self.kind        = 'line'
        self.stacked     = False
        self.cum         = False
        self.grouper     = None
        self.focus       = None
        self.filter      = None
        self.rows        = None
        self.cols        = None
        self.xaxis       = None
        self.xticklabels = None


    def plot(self, legend=True, **kwargs):
        """
        Plot trendlines from the data.
        Pass in parameters to change plot settings.
        Any changes will be stored within the object.

        Fields that contain categorical variables may be used to split the
        graph into subplots by assigning them to either `rows` or `cols`.
        Assign a categorical variable to `grouper` to plot multiple groups
        within a single graph. Focus can be used to highlight one of the groups.
        """

        for kw, value in kwargs.copy().items():
            if kw in [
                'start',
                'end',
                'period',
                'kind',
                'stacked',
                'cum',
                'grouper',
                'focus',
                'filter',
                'rows',
                'cols',
                'xaxis',
                'xticklabels',
            ]:
                setattr(self, kw, value)
                del kwargs[kw]

        layout = {**self.layout_general, **kwargs}
        if self.nrows > 1 or self.ncols > 1:
            fig = self._subplot(**kwargs, **layout)
        else:
            ax = self._plot(self.data, **layout)
            fig = self._resize_subplots(ax.figure)
        self._figure = fig
        return fig


    def _plot(self, data, row=None, col=None, legend=True, **kwargs):
        data = self.get_cross_section(data, row=row, col=col)

        if self.grouper is not None and self.focus is not None:
            if not self.focus in self.groups:
                self.focus = None
        if self.focus is not None:
            ax = self._plot_with_focus(data, **kwargs)
        else:
            ax = data.plot(
                kind    = self.kind,
                stacked = self.stacked,
                style   = self.styling,
                legend  = False,
                **kwargs)

        if self.xticklabels is not None:
            ax.set_xticklabels(self.xticklabels)

        if legend:
            lines, labels = ax.get_legend_handles_labels()
            ax.legend(
                reversed(lines),
                reversed(labels),
                title=self.grouper
            )
        return ax


    def _plot_with_focus(self, data, **kwargs):
        if 'ax' in kwargs:
            _ax = kwargs['ax']
            del kwargs['ax']
        else:
            _ax = None

        layout_comparison = {**self.layout_comparison, **kwargs}
        ax = data.drop(self.focus, axis=1).plot(
            ax      = _ax,
            kind    = self.kind,
            stacked = self.stacked,
            style   = self.styling,
            legend  = False,
            **layout_comparison,
        )
        ax = data[self.focus].plot(
            ax      = ax,
            kind    = self.kind,
            stacked = self.stacked,
            style   = self.styling,
            legend  = False,
            **kwargs,
        )
        return ax


    def _subplot(
        self,
        sharex = True,
        sharey = False,
        legend = True,
        **kwargs,
    ):

        if self.rows is None and self.cols is None:
            raise ValueError("Rows and cols cannot both be None.")

        fig, axes = plt.subplots(
            self.nrows,
            self.ncols,
            sharex=sharex,
            sharey=sharey,
            constrained_layout=True,
        )

        data = self.data
        if self.ncols == 1:
            for i, row in enumerate(self.row_values):
                self._plot(
                    data,
                    ax     = axes[i],
                    row    = row,
                    col    = None,
                    legend = False,
                    **kwargs,
                )
            for ax, row in zip(axes, self.row_values):
                ax.set_ylabel(row, rotation=0, size='large', labelpad=36)
        elif self.nrows == 1:
            for i, col in enumerate(self.col_values):
                self._plot(
                    data,
                    ax     = axes[i],
                    row    = None,
                    col    = col,
                    legend = False,
                    **kwargs,
                )
            for ax, col in zip(axes, self.col_values):
                ax.set_title(col)
        else:
            for i, row in enumerate(self.row_values):
                for j, col in enumerate(self.col_values):
                    self._plot(
                        data,
                        ax     = axes[i,j],
                        row    = row,
                        col    = col,
                        legend = False,
                        **kwargs,
                    )
            for ax, col in zip(axes[0], self.col_values):
                ax.set_title(col)
            for ax, row in zip(axes[:,0], self.row_values):
                ax.set_ylabel(row, rotation=0, size='large', labelpad=36)

        if legend:
            handles = []
            labels = []
            for ax in fig.axes:
                for handle, label in zip(*ax.get_legend_handles_labels()):
                    if label not in labels:
                        handles.append(handle)
                        labels.append(label)
            fig.legend(
                reversed(handles),
                reversed(labels),
                title          = self.grouper,
                loc            = 'upper left',
                bbox_to_anchor = (1.0, 1.0),
                bbox_transform = plt.gcf().transFigure,
            )

            # PYTHON >= 3.7
            # legend_entries = {
            #     label: handle
            #     for ax in fig.axes
            #     for handle, label in zip(*ax.get_legend_handles_labels())
            # }
            # fig.legend(
            #     reversed(legend_entries.values()),
            #     reversed(legend_entries.keys()),
            #     title          = self.grouper,
            #     loc            = 'upper left',
            #     bbox_to_anchor = (1.0, 1.0),
            #     bbox_transform = plt.gcf().transFigure,
            # )

        fig = self._resize_subplots(fig)
        return fig


    def _resize_subplots(self, fig):
        rows, cols, _, _ = fig.axes[0].get_subplotspec().get_geometry()
        ax_width = fig.axes[0].get_window_extent().width
        ax_height = fig.axes[0].get_window_extent().height

        missing_width  = self.width - ax_width / fig.dpi
        missing_height = self.height - ax_height / fig.dpi

        new_width  = (cols * missing_width) + fig.get_figwidth()
        new_height = (rows * missing_height) + fig.get_figheight()

        fig.set_size_inches(new_width, new_height)
        return fig


    def _repr_html_(self):
        _ts = self._ts
        ts = self.ts
        elements = dict(
            timeseries = dict(
                xaxis       = self.xaxis,
                grouper     = self.grouper,
                focus       = self.focus,
                period      = self.period,
                shape       = _ts.shape,
                min         = _ts.index.min(),
                max         = _ts.index.max(),
            ),
            filter = dict(
                filter      = self.filter,
                start       = self.start,
                end         = self.end,
                shape       = ts.shape,
                min         = ts.index.min(),
                max         = ts.index.max(),
            ),
            graph = dict(
                kind        = self.kind,
                stacked     = self.stacked,
                cumulative  = self.cum,
            ),
            subplots = dict(
                rows        = self.rows,
                n_rows      = self.nrows,
                row_values  = self.row_values,
                cols        = self.cols,
                n_cols      = self.ncols,
                col_values  = self.col_values,
            ),
            layout = dict(
                width       = self.width,
                height      = self.height,
                xticklabels = self.xticklabels,
                general     = self.layout_general,
                comparison  = self.layout_comparison,
            ),
        )

        tables = [
            pd.Series(dct, name=key).to_frame().to_html()
            for key, dct in elements.items()
        ]

        return (
            "<div style='display: flex; gap: 12px;'>"
            f"{''.join(tables)}"
            "</div>"
        )


    @classmethod
    def from_df(cls, df, datefield, yearfield, year, **kwargs):
        ts = timeseries_offset(df, datefield, yearfield, year)
        return cls(ts, **kwargs)


    @staticmethod
    def get_values(s):
        if isinstance(s.dtypes, pd.CategoricalDtype):
            s = s.cat.remove_unused_categories()
            values = s.cat.categories.to_list()
        else:
            values = sorted(s.unique())
        return values


    @staticmethod
    def get_cross_section(data, row=None, col=None):
        if row is not None and col is not None:
            return data.xs([row, col])
        elif row is not None:
            return data.xs(row)
        elif col is not None:
            return data.xs(col)
        else:
            return data
