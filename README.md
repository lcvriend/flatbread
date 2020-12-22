# <img src="static/noun_pita_3216932.svg" width="24"> Flatbread <img src="static/noun_pita_3216932.svg" width="24">

## About
Flatbread is a small library built to extend the pivot table functionality in pandas. The library contains functions which will allow you to easily add **totals/subtotals** to one or more axes/levels of your pivot table. Furthermore, flatbread can calculate **percentages** from the totals/subtotals of each axis/level of your pivot table. You can transform the existing values in your table into percentages, but you can also add the percentages neatly next to your data. If the required (sub)totals are not present, then flatbread will add them automatically in order to perform the calculations. By default the (sub)totals are kept but you can drop them too. The library also contains some functionality built on top of matplotlib for plotting your data.

## Name
Initially I planned for this library to be called pita -- short for pivot tables. But as that name was already taken on pypi.org the choice fell on flatbread.

## Install
To install:

```
pip install flatbread
```

## Pivot tables
Let's create a df for testing:

```Python
from random import randint
import pandas as pd
import flatbread as fb

df = pd._testing.makeCustomDataframe(
    nrows=8,
    ncols=4,
    data_gen_f=lambda r,c:randint(1,100),
    c_idx_nlevels=2,
    r_idx_nlevels=3,
    c_ndupe_l=[2,1],
    r_ndupe_l=[4,2,1],
)
```

### Totals and subtotals
Flatbread let's you easily add subtotals to your pivot tables. Here we add totals and subtotals to both axes at once:

```
df.pipe(fb.totals.add, axis=2, level=[0,1])
```

<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>C0</th>
      <th colspan="3" halign="left">C_l0_g0</th>
      <th colspan="3" halign="left">C_l0_g1</th>
      <th>Total</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C1</th>
      <th>C_l1_g0</th>
      <th>C_l1_g1</th>
      <th>Subtotal</th>
      <th>C_l1_g2</th>
      <th>C_l1_g3</th>
      <th>Subtotal</th>
      <th></th>
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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">R_l0_g0</th>
      <th rowspan="2" valign="top">R_l1_g0</th>
      <th>R_l2_g0</th>
      <td align="right">77</td>
      <td align="right">1</td>
      <td align="right">78</td>
      <td align="right">59</td>
      <td align="right">40</td>
      <td align="right">99</td>
      <td align="right">177</td>
    </tr>
    <tr>
      <th>R_l2_g1</th>
      <td align="right">69</td>
      <td align="right">83</td>
      <td align="right">152</td>
      <td align="right">27</td>
      <td align="right">85</td>
      <td align="right">112</td>
      <td align="right">264</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">R_l1_g1</th>
      <th>R_l2_g2</th>
      <td align="right">18</td>
      <td align="right">9</td>
      <td align="right">27</td>
      <td align="right">72</td>
      <td align="right">52</td>
      <td align="right">124</td>
      <td align="right">151</td>
    </tr>
    <tr>
      <th>R_l2_g3</th>
      <td align="right">24</td>
      <td align="right">85</td>
      <td align="right">109</td>
      <td align="right">10</td>
      <td align="right">44</td>
      <td align="right">54</td>
      <td align="right">163</td>
    </tr>
    <tr>
      <th>Subtotal</th>
      <th></th>
      <td align="right">188</td>
      <td align="right">178</td>
      <td align="right">366</td>
      <td align="right">168</td>
      <td align="right">221</td>
      <td align="right">389</td>
      <td align="right">755</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">R_l0_g1</th>
      <th rowspan="2" valign="top">R_l1_g2</th>
      <th>R_l2_g4</th>
      <td align="right">27</td>
      <td align="right">47</td>
      <td align="right">74</td>
      <td align="right">39</td>
      <td align="right">70</td>
      <td align="right">109</td>
      <td align="right">183</td>
    </tr>
    <tr>
      <th>R_l2_g5</th>
      <td align="right">24</td>
      <td align="right">27</td>
      <td align="right">51</td>
      <td align="right">12</td>
      <td align="right">88</td>
      <td align="right">100</td>
      <td align="right">151</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">R_l1_g3</th>
      <th>R_l2_g6</th>
      <td align="right">64</td>
      <td align="right">30</td>
      <td align="right">94</td>
      <td align="right">27</td>
      <td align="right">40</td>
      <td align="right">67</td>
      <td align="right">161</td>
    </tr>
    <tr>
      <th>R_l2_g7</th>
      <td align="right">96</td>
      <td align="right">9</td>
      <td align="right">105</td>
      <td align="right">82</td>
      <td align="right">59</td>
      <td align="right">141</td>
      <td align="right">246</td>
    </tr>
    <tr>
      <th>Subtotal</th>
      <th></th>
      <td align="right">211</td>
      <td align="right">113</td>
      <td align="right">324</td>
      <td align="right">160</td>
      <td align="right">257</td>
      <td align="right">417</td>
      <td align="right">741</td>
    </tr>
    <tr>
      <th>Total</th>
      <th></th>
      <th></th>
      <td align="right">399</td>
      <td align="right">291</td>
      <td align="right">690</td>
      <td align="right">328</td>
      <td align="right">478</td>
      <td align="right">806</td>
      <td align="right">1496</td>
    </tr>
  </tbody>
</table>

### Percentages from totals and subtotals
Flatbread let's you calculate the percentages from within a specified level of your data. You can transform the data or add the percentages into your pivot table:

```Python
df.pipe(fb.percs.add, level=1)
```

<table border="1" class="dataframe">
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
      <th></th>
      <th>abs</th>
      <th>%</th>
      <th>abs</th>
      <th>%</th>
      <th>abs</th>
      <th>%</th>
      <th>abs</th>
      <th>%</th>
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
      <td align="right">77</td>
      <td align="right">41.0</td>
      <td align="right">1</td>
      <td align="right">0.6</td>
      <td align="right">59</td>
      <td align="right">35.1</td>
      <td align="right">40</td>
      <td align="right">18.1</td>
    </tr>
    <tr>
      <th>R_l2_g1</th>
      <td align="right">69</td>
      <td align="right">36.7</td>
      <td align="right">83</td>
      <td align="right">46.6</td>
      <td align="right">27</td>
      <td align="right">16.1</td>
      <td align="right">85</td>
      <td align="right">38.5</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">R_l1_g1</th>
      <th>R_l2_g2</th>
      <td align="right">18</td>
      <td align="right">9.6</td>
      <td align="right">9</td>
      <td align="right">5.1</td>
      <td align="right">72</td>
      <td align="right">42.9</td>
      <td align="right">52</td>
      <td align="right">23.5</td>
    </tr>
    <tr>
      <th>R_l2_g3</th>
      <td align="right">24</td>
      <td align="right">12.8</td>
      <td align="right">85</td>
      <td align="right">47.8</td>
      <td align="right">10</td>
      <td align="right">6.0</td>
      <td align="right">44</td>
      <td align="right">19.9</td>
    </tr>
    <tr>
      <th>Subtotal</th>
      <th></th>
      <td align="right">188</td>
      <td align="right">100.0</td>
      <td align="right">178</td>
      <td align="right">100.0</td>
      <td align="right">168</td>
      <td align="right">100.0</td>
      <td align="right">221</td>
      <td align="right">100.0</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">R_l0_g1</th>
      <th rowspan="2" valign="top">R_l1_g2</th>
      <th>R_l2_g4</th>
      <td align="right">27</td>
      <td align="right">12.8</td>
      <td align="right">47</td>
      <td align="right">41.6</td>
      <td align="right">39</td>
      <td align="right">24.4</td>
      <td align="right">70</td>
      <td align="right">27.2</td>
    </tr>
    <tr>
      <th>R_l2_g5</th>
      <td align="right">24</td>
      <td align="right">11.4</td>
      <td align="right">27</td>
      <td align="right">23.9</td>
      <td align="right">12</td>
      <td align="right">7.5</td>
      <td align="right">88</td>
      <td align="right">34.2</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">R_l1_g3</th>
      <th>R_l2_g6</th>
      <td align="right">64</td>
      <td align="right">30.3</td>
      <td align="right">30</td>
      <td align="right">26.5</td>
      <td align="right">27</td>
      <td align="right">16.9</td>
      <td align="right">40</td>
      <td align="right">15.6</td>
    </tr>
    <tr>
      <th>R_l2_g7</th>
      <td align="right">96</td>
      <td align="right">45.5</td>
      <td align="right">9</td>
      <td align="right">8.0</td>
      <td align="right">82</td>
      <td align="right">51.2</td>
      <td align="right">59</td>
      <td align="right">23.0</td>
    </tr>
    <tr>
      <th>Subtotal</th>
      <th></th>
      <td align="right">211</td>
      <td align="right">100.0</td>
      <td align="right">113</td>
      <td align="right">100.0</td>
      <td align="right">160</td>
      <td align="right">100.0</td>
      <td align="right">257</td>
      <td align="right">100.0</td>
    </tr>
  </tbody>
</table>

### Localize your table formats
Using the `format` function your pivot table will nicely be displayed according to your preferred locale:

```
df = pd._testing.makeCustomDataframe(
    nrows=5,
    ncols=4,
    data_gen_f=lambda r,c:randint(10,1000),
    c_idx_nlevels=1,
    r_idx_nlevels=1,
)

df.pipe(fb.percs.add).pipe(fb.format)
```

<table border="1" class="dataframe">
  <thead>
    <tr>
      <th>C0</th>
      <th colspan="2" halign="left">C_l0_g0</th>
      <th colspan="2" halign="left">C_l0_g1</th>
      <th colspan="2" halign="left">C_l0_g2</th>
      <th colspan="2" halign="left">C_l0_g3</th>
    </tr>
    <tr>
      <th></th>
      <th>abs</th>
      <th>%</th>
      <th>abs</th>
      <th>%</th>
      <th>abs</th>
      <th>%</th>
      <th>abs</th>
      <th>%</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>R_l0_g0</th>
      <td align="right">773</td>
      <td align="right">22,9</td>
      <td align="right">892</td>
      <td align="right">23,4</td>
      <td align="right">968</td>
      <td align="right">29,1</td>
      <td align="right">294</td>
      <td align="right">19,9</td>
    </tr>
    <tr>
      <th>R_l0_g1</th>
      <td align="right">979</td>
      <td align="right">28,9</td>
      <td align="right">457</td>
      <td align="right">12,0</td>
      <td align="right">662</td>
      <td align="right">19,9</td>
      <td align="right">221</td>
      <td align="right">15,0</td>
    </tr>
    <tr>
      <th>R_l0_g2</th>
      <td align="right">495</td>
      <td align="right">14,6</td>
      <td align="right">917</td>
      <td align="right">24,0</td>
      <td align="right">890</td>
      <td align="right">26,8</td>
      <td align="right">63</td>
      <td align="right">4,3</td>
    </tr>
    <tr>
      <th>R_l0_g3</th>
      <td align="right">282</td>
      <td align="right">8,3</td>
      <td align="right">826</td>
      <td align="right">21,7</td>
      <td align="right">681</td>
      <td align="right">20,5</td>
      <td align="right">804</td>
      <td align="right">54,5</td>
    </tr>
    <tr>
      <th>R_l0_g4</th>
      <td align="right">853</td>
      <td align="right">25,2</td>
      <td align="right">722</td>
      <td align="right">18,9</td>
      <td align="right">120</td>
      <td align="right">3,6</td>
      <td align="right">94</td>
      <td align="right">6,4</td>
    </tr>
    <tr>
      <th>Total</th>
      <td align="right">3.382</td>
      <td align="right">100,0</td>
      <td align="right">3.814</td>
      <td align="right">100,0</td>
      <td align="right">3.321</td>
      <td align="right">100,0</td>
      <td align="right">1.476</td>
      <td align="right">100,0</td>
    </tr>
  </tbody>
</table>

### Easy configuration
Flatbread let's you control most of its behavior through key-word arguments, but it is also easy to store your settings and use them globally throughout a project:

```
from flatbread import CONFIG

# pick your preferred locale and set it
CONFIG.format['locale'] = 'nl_NL'
CONFIG.set_locale()

# set your own labels
CONFIG.aggregation['totals_name'] = 'Totes'

# store your configuration permanently
CONFIG.save()

# restore to factory settings
CONFIG.factory_reset()
```

## Pivot charts

Use the Trendline object to create trendlines. Compare multiple years:

```Python
tl = fb.TrendLine.from_df(
    sample,
    offset_year = 2019,
    datefield   = 'Date of Application',
    yearfield   = 'Academic Year',
    period      = 'w',
    end         = '2019-09-01',
    grouper     = 'Academic Year',
    focus       = 2019,
)

fig = tl.plot()
```

<img src="static/2020-12-22.Date_of_Application.line.abs.svg" width="630">

Split your graphs in rows and columns:

```Python
tl = fb.TrendLine.from_df(
    sample,
    offset_year = 2019,
    datefield   = 'Date Processed',
    yearfield   = 'Academic Year',
    period      = 'w',
    end         = '2019-10-01',
    grouper     = 'Faculty',
    focus       = 'Humanities',
)

fig = tl.plot(
    rows   = 'Origin Country',
    cols   = 'Examination Type',
    cum    = True,
    filter = "`Academic Year` == 2019"
)
```

<img src="static/2020-12-22.Date_Processed.line.cum.svg">
