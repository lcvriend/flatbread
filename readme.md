# Flatbread

## About
Flatbread is a small library which adds some pivot-table-like functionality to pandas. Flatbread is accessible through the `DataFrame` and `Series` using the `pita` accessor.

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
Flatbread let's you easily add totals and subtotals to your pivot tables:

```
df.pita.add_totals().pita.add_subtotals(axis=2, levels=0)
```

<table border="1" class="dataframe">
  <thead>
    <tr>
      <th></th>
      <th></th>
      <th>C0</th>
      <th colspan="3" halign="left">C_l0_g0</th>
      <th colspan="3" halign="left">C_l0_g1</th>
    </tr>
    <tr>
      <th></th>
      <th></th>
      <th>C1</th>
      <th>C_l1_g0</th>
      <th>C_l1_g1</th>
      <th>Subtotals</th>
      <th>C_l1_g2</th>
      <th>C_l1_g3</th>
      <th>Subtotals</th>
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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">R_l0_g0</th>
      <th rowspan="2" valign="top">R_l1_g0</th>
      <th>R_l2_g0</th>
      <td>16.0</td>
      <td>4.0</td>
      <td>20.0</td>
      <td>34.0</td>
      <td>59.0</td>
      <td>93.0</td>
    </tr>
    <tr>
      <th>R_l2_g1</th>
      <td>49.0</td>
      <td>51.0</td>
      <td>100.0</td>
      <td>33.0</td>
      <td>10.0</td>
      <td>43.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">R_l1_g1</th>
      <th>R_l2_g2</th>
      <td>10.0</td>
      <td>46.0</td>
      <td>56.0</td>
      <td>43.0</td>
      <td>82.0</td>
      <td>125.0</td>
    </tr>
    <tr>
      <th>R_l2_g3</th>
      <td>98.0</td>
      <td>62.0</td>
      <td>160.0</td>
      <td>81.0</td>
      <td>28.0</td>
      <td>109.0</td>
    </tr>
    <tr>
      <th>Subtotals</th>
      <th></th>
      <td>173.0</td>
      <td>163.0</td>
      <td>336.0</td>
      <td>191.0</td>
      <td>179.0</td>
      <td>370.0</td>
    </tr>
    <tr>
      <th rowspan="4" valign="top">R_l0_g1</th>
      <th rowspan="2" valign="top">R_l1_g2</th>
      <th>R_l2_g4</th>
      <td>99.0</td>
      <td>17.0</td>
      <td>116.0</td>
      <td>50.0</td>
      <td>99.0</td>
      <td>149.0</td>
    </tr>
    <tr>
      <th>R_l2_g5</th>
      <td>17.0</td>
      <td>91.0</td>
      <td>108.0</td>
      <td>51.0</td>
      <td>36.0</td>
      <td>87.0</td>
    </tr>
    <tr>
      <th>R_l1_g3</th>
      <th>R_l2_g6</th>
      <td>78.0</td>
      <td>81.0</td>
      <td>159.0</td>
      <td>77.0</td>
      <td>53.0</td>
      <td>130.0</td>
    </tr>
    <tr>
      <th>Subtotals</th>
      <th></th>
      <td>194.0</td>
      <td>189.0</td>
      <td>383.0</td>
      <td>178.0</td>
      <td>188.0</td>
      <td>366.0</td>
    </tr>
    <tr>
      <th>Totals</th>
      <th></th>
      <th></th>
      <td>367.0</td>
      <td>352.0</td>
      <td>719.0</td>
      <td>369.0</td>
      <td>367.0</td>
      <td>736.0</td>
    </tr>
  </tbody>
</table>
