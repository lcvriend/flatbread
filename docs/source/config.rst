.. highlight:: python

Configuration
=============

Flatbread let's you control most of its behavior through key-word arguments, but it is also easy to store your settings and use them globally throughout a project using :py:obj:`flatbread.config.CONFIG` which is an instance of the :py:class:`flatbread.config.Config` class.

Example
-------

Here is a small example::

    from flatbread.build.test import (
        dataset_categoricals,
        dataset_numbers,
    )
    from flatbread import CONFIG

    # pick your preferred locale and set it (used with `format`)
    CONFIG.format['locale'] = 'nl_NL'
    CONFIG.set_locale()

    # set your own labels
    CONFIG.aggregation['totals_name'] = 'Totes'
    CONFIG.aggregation['label_rel'] = 'pct'

    # define the number of digits to round to (-1 is no rounding)
    CONFIG.aggregation['ndigits'] = 2

    # make a dataset
    k = 10000
    df = dataset_categoricals([3., 2., 4, 3], k=k
    ).join(dataset_numbers([250, 1.], k=k)
    ).assign(
        A = lambda df: df.A.str.upper(),
        num_cat = lambda df: pd.cut(df.int0, [0,75,125,250]),
    )

    # present as pivot table
    df.pita(
        columns=['A'],
        index=['B', 'D'],
        na='hide',
    ).percs(how='add')

.. raw:: html
   :file: _examples/ex_config.html

Defaults
--------
It is possible to save your settings (and also to reset to the default)::

    # store your configuration permanently (across sessions)
    CONFIG.save()

    # restore your settings to 'factory' defaults
    CONFIG.factory_reset()

This is flatbread's default configuration:

.. literalinclude:: ../../flatbread/config.defaults.json
