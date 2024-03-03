import pandas as pd

std_parties = ["con","lab","lib","ref","nat","oth"]

def standardise_df(df, col_dict):
    ndf = df.copy()
    ndf["con"] = df[col_dict["Con"]]
    ndf["lab"] = df[col_dict["Lab"]]
    ndf["lib"] = df[col_dict["Lib"]]
    if "Ref" in col_dict.keys():
        ndf["ref"] = df[col_dict["Ref"]]
    if "Nat" in col_dict.keys():
        ndf["nat"] = df[col_dict["Nat"]]
    ndf["oth"] = df[col_dict["Oth"]]
    return ndf  

def get_GB_res(df, yr=2019):
    res_df = pd.DataFrame({
        "con":[df[str(yr)+"_Resultscon"].sum()],
        "lab":[df[str(yr)+"_Resultslab"].sum()],
        "lib":[df[str(yr)+"_Resultslib"].sum()],
        "ref":[df[str(yr)+"_Resultsref"].sum()],
        "nat":[df[str(yr)+"_Resultsnat"].sum()],
        "oth":[df[str(yr)+"_Resultsoth"].sum()],

    })
    return res_df

def convert_to_pc(df):
    tot = df.sum(axis=1)
    for c in df.columns:
        df[c] = df[c]/tot
    return df