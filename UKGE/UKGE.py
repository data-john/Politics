import pandas as pd
from polls import *
import numpy as np
import datetime






std_parties = ["con","lab","lib","ref","nat","oth"]



def run_sim(n=1000):
    poll_avgs = get_poll_avgs()
    pc_results = get_results_percentages()


def get_poll_avgs():
    poll_avg19 = get_weighted_poll_avg(url_19, col_dict=col_dict19)
    poll_avg17 = get_weighted_poll_avg(url_17, col_dict=col_dict17)
    poll_avg15 = get_weighted_poll_avg(url_15, col_dict=col_dict15)
    poll_avg10 = get_weighted_poll_avg(url_10, col_dict=col_dict10)
    poll_avg05 = get_weighted_poll_avg(url_05, col_dict=col_dict05)
    poll_avg19 = standardise_df(poll_avg19, col_dict19)
    poll_avg17 = standardise_df(poll_avg17, col_dict17)
    poll_avg15 = standardise_df(poll_avg15, col_dict15)
    poll_avg10 = standardise_df(poll_avg10, col_dict10)
    poll_avg05 = standardise_df(poll_avg05, col_dict05)
    poll_avgs = [poll_avg05,poll_avg10,poll_avg15,poll_avg17,poll_avg19]
    return poll_avgs

def get_results_percentages():
    gb19 = get_GB_res(df)
    pc_res_19 = convert_to_pc(gb19)
    gb17 = get_GB_res(df,yr=2017)
    pc_res_17 = convert_to_pc(gb17)
    gb15 = get_GB_res(df,yr=2015)
    pc_res_15 = convert_to_pc(gb15)
    gb10 = get_GB_res(df,yr=2010)
    pc_res_10 = convert_to_pc(gb10)
    gb05 = get_GB_res(df,yr=2005)
    pc_res_05 = convert_to_pc(gb05)
    pc_results = [pc_res_05,pc_res_10,pc_res_15,pc_res_17,pc_res_19]
    return pc_results

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