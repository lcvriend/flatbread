from random import randint
import pandas as pd

def build_multiindex_df()
    df = pd._testing.makeCustomDataframe(
        nrows=6,
        ncols=4,
        data_gen_f=lambda r,c:randint(1,100),
        c_idx_nlevels=2,
        r_idx_nlevels=2,
        c_ndupe_l=[2,1],
        r_ndupe_l=[2,1],
        )
    df2 = df.copy()
    df2.index = df.index.set_levels(['R_l0_g1'], level=0)
    df.append(df2)
