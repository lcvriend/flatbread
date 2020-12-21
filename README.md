# Flatbread

## Name
Initially I planned for this library to be called pita -- short for pivot tables. But as that name was already taken on pypi.org the choice fell on flatbread.

## About
Flatbread is a library built upon pandas and matplotlib for displaying and presenting data. It is currently a work in progress. The goal is to implement the same functionalities as [pandas crosstabs](https://github.com/lcvriend/pandas_crosstabs).

## Install
To install:

```pip install flatbread```

## Pivot tables
Easily add subtotals to your pivot tables:

```Python
from random import randint
import pandas as pd
import flatbread

df = pd._testing.makeCustomDataframe(
    nrows=8,
    ncols=4,
    data_gen_f=lambda r,c:randint(1,100),
    c_idx_nlevels=3,
    r_idx_nlevels=3,
    c_ndupe_l=[4,2,1],
    r_ndupe_l=[4,2,1],
)

df.pipe(flatbread.agg.totals.add, axis=1, level=1)
```

![example table](static/example_subtotals.png)

Add percentages to your pivot tables:


```Python
df.pipe(
    flatbread.agg.totals.add, axis=2
).pipe(
    flatbread.agg.percentages.add
)
```

![example table](static/example_percentages.png)

## Pivot charts

Use the Trendline object to create trendlines. Compare multiple years:

```Python
tl = flatbread.TrendLine.from_df(
    df,
    year      = 2019,
    yearfield = 'academic_year',
    datefield = 'date_request',
    end       = '2019-09-01',
    period    = 'w',
    grouper   = 'academic_year',
    focus     = 2019,
)

fig = tl.plot()
tl.savefig()
```

![example graph](static/2020-08-26.date_request.line.abs.p[w].g[academic_year].e[2019-09-01].png)

Split your graphs in rows and columns:

```Python
tl = flatbread.TrendLine.from_df(
    sample.query(query),
    year      = 2019,
    datefield = 'date_enrolled',
    yearfield = 'academic_year',
    period    = 'w',
    end       = '2019-10-01',
    grouper   = 'faculty',
    focus     = 'Humanities',
)

fig = tl.plot(
    rows   = 'origin',
    cols   = 'exam_type',
    cum    = True,
    filter = "academic_year == 2019"
)
tl.savefig()
```

![example graph](static/2020-08-26.date_enrolled.line.cum.p[w].g[faculty].r[origin].c[exam_type].e[2019-10-01].f[academic_year==2019].png)

### HTML TEST

<table border="1" cellpadding="4" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>C0</th>
      <th colspan="4" halign="left">C_l0_g0</th>
      <th colspan="4" halign="left">C_l0_g1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C1</th>
      <th colspan="2" halign="left">C_l1_g0</th>
      <th colspan="2" halign="left">C_l1_g1</th>
      <th colspan="2" halign="left">C_l1_g2</th>
      <th colspan="2" halign="left">C_l1_g3</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C2</th>
      <th>C_l2_g0</th>
      <th>C_l2_g1</th>
      <th>C_l2_g2</th>
      <th>C_l2_g3</th>
      <th>C_l2_g4</th>
      <th>C_l2_g5</th>
      <th>C_l2_g6</th>
      <th>C_l2_g7</th>
    </tr>
    <tr>
      <th>R0</th>
      <th>R1</th>
      <th>R2</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">R_l0_g0</th>
      <th rowspan="2" valign="top">R_l1_g0</th>
      <th>R_l2_g0</th>
      <td align="right">45</td>
      <td align="right">68</td>
      <td align="right">78</td>
      <td align="right">52</td>
      <td align="right">6</td>
      <td align="right">25</td>
      <td align="right">99</td>
      <td align="right">42</td>
    </tr>
    <tr>
      <th>R_l2_g1</th>
      <td align="right">63</td>
      <td align="right">86</td>
      <td align="right">97</td>
      <td align="right">88</td>
      <td align="right">60</td>
      <td align="right">20</td>
      <td align="right">24</td>
      <td align="right">10</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">R_l1_g1</th>
      <th>R_l2_g2</th>
      <td align="right">92</td>
      <td align="right">33</td>
      <td align="right">44</td>
      <td align="right">41</td>
      <td align="right">95</td>
      <td align="right">48</td>
      <td align="right">36</td>
      <td align="right">25</td>
    </tr>
    <tr>
      <th>R_l2_g3</th>
      <td align="right">88</td>
      <td align="right">80</td>
      <td align="right">67</td>
      <td align="right">20</td>
      <td align="right">28</td>
      <td align="right">83</td>
      <td align="right">96</td>
      <td align="right">38</td>
    </tr>
    <tr>
      <th>Subtotal</th>
      <th></th>
      <td align="right">288</td>
      <td align="right">267</td>
      <td align="right">286</td>
      <td align="right">201</td>
      <td align="right">189</td>
      <td align="right">176</td>
      <td align="right">255</td>
      <td align="right">115</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">R_l0_g1</th>
      <th rowspan="2" valign="top">R_l1_g2</th>
      <th>R_l2_g4</th>
      <td align="right">90</td>
      <td align="right">28</td>
      <td align="right">39</td>
      <td align="right">76</td>
      <td align="right">2</td>
      <td align="right">88</td>
      <td align="right">18</td>
      <td align="right">47</td>
    </tr>
    <tr>
      <th>R_l2_g5</th>
      <td align="right">19</td>
      <td align="right">76</td>
      <td align="right">37</td>
      <td align="right">5</td>
      <td align="right">38</td>
      <td align="right">59</td>
      <td align="right">88</td>
      <td align="right">7</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">R_l1_g3</th>
      <th>R_l2_g6</th>
      <td align="right">20</td>
      <td align="right">19</td>
      <td align="right">20</td>
      <td align="right">4</td>
      <td align="right">8</td>
      <td align="right">59</td>
      <td align="right">64</td>
      <td align="right">11</td>
    </tr>
    <tr>
      <th>R_l2_g7</th>
      <td align="right">90</td>
      <td align="right">35</td>
      <td align="right">25</td>
      <td align="right">29</td>
      <td align="right">13</td>
      <td align="right">22</td>
      <td align="right">2</td>
      <td align="right">55</td>
    </tr>
    <tr>
      <th>Subtotal</th>
      <th></th>
      <td align="right">219</td>
      <td align="right">158</td>
      <td align="right">121</td>
      <td align="right">114</td>
      <td align="right">61</td>
      <td align="right">228</td>
      <td align="right">172</td>
      <td align="right">120</td>
    </tr>
    <tr>
      <th>Total</th>
      <th></th>
      <th></th>
      <td align="right">507</td>
      <td align="right">425</td>
      <td align="right">407</td>
      <td align="right">315</td>
      <td align="right">250</td>
      <td align="right">404</td>
      <td align="right">427</td>
      <td align="right">235</td>
    </tr>
  </tbody>
</table>
