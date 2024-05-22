import pandas as pd
from polls import *
import numpy as np
import datetime


election_day = datetime.date(2024,7,4)



std_parties = ["con","lab","lib","ref","nat","oth"]
def create_output(results_path = "UKGE/outputs/results/Results_"):
    today = datetime.date.today()
    df = pd.read_csv(results_path+str(today)+".csv")
    df = df.transpose()
    df.columns = df.loc["Unnamed: 0"]
    df = df.drop("Unnamed: 0")
    seat_cols = ["conSeats","labSeats","libSeats","refSeats","natSeats","othSeats"]
    df[seat_cols] = df[seat_cols].astype(int)
    sims = len(df)
    reasonable_res = ["lab", "Hung Parliament: Largest Party lab", "Hung Parliament: Largest Party con", "con"]
    res_dict = {}
    for res in reasonable_res:
        if res in df["Result"].value_counts().index:
            res_dict[res] = [df["Result"].value_counts()[res] / sims]
        else:
            res_dict[res] = 0
    med_df = df[(df["conSeats"]>=df["conSeats"].quantile(0.485))&(df["conSeats"]<=df["conSeats"].quantile(0.515))&(df["labSeats"]>=df["labSeats"].quantile(0.485))&(df["labSeats"]<=df["labSeats"].quantile(0.515))]
    typical_run = med_df[(med_df["natSeats"]>=med_df["natSeats"].quantile(0.3))&(med_df["natSeats"]<=med_df["natSeats"].quantile(0.7))&(med_df["libSeats"]>=med_df["libSeats"].quantile(0.3))&(med_df["libSeats"]<=med_df["libSeats"].quantile(0.7))&(med_df["refSeats"]>=med_df["refSeats"].quantile(0.3))&(med_df["refSeats"]<=med_df["refSeats"].quantile(0.7))].copy()
    for c in seat_cols:
        res_dict[c] = [typical_run.iloc[0][c]]
    # Add Poll of Polls
    polls = get_weighted_poll_avg(next_url, col_dict=next_col_dict)
    for p in polls.keys():
        res_dict[p] = [round(polls[p],ndigits=3)]
    # Add Latest Polls
    latest_polls = get_latest_polls_dict()
    for p in latest_polls.keys():
        res_dict[p] = [round(latest_polls[p], ndigits=3)]
    today_df = pd.DataFrame(res_dict).rename({0:str(datetime.date.today())}).transpose()
    # today_df.to_csv("UKGE/outputs/EXPORT.csv")
    return today_df

def update_export(from_path="outputs/EXPORT.csv", to_path="outputs/EXPORT.csv", results_path = "UKGE/outputs/results/Results_"):
    today_df = create_output(results_path)
    from_df = pd.read_csv(from_path)
    from_df = from_df.set_index("Unnamed: 0")  
    from_df[str(datetime.date.today())] = today_df[str(datetime.date.today())]
    from_df.to_csv(to_path)
    return from_df

def run_sim(n=1000, res_path = "UKGE/outputs/resultsclusteredconstituencies.csv", output_path="UKGE/outputs/results/Results_", polls_to_path="UKGE/outputs/lastnatpolls.csv"):
    df = pd.read_csv(res_path)
    # poll_avgs = get_poll_avgs()
    pc_results = get_results_percentages(df.copy())
    pc_res_19 = pc_results[-1]
    constituencies = list(df["New constituency name"])

    next_poll_avg = get_weighted_poll_avg(next_url, col_dict=next_col_dict)
    next_poll_avg.to_csv(polls_to_path, index=False)
    nat_polls = standardise_df(next_poll_avg, next_col_dict)
    chg_df = nat_polls - pc_res_19
    chg_df = chg_df.dropna(axis=1).copy()

    natchgs = []
    sims_num = n
    today = datetime.date.today()
    base_seed = int(today.strftime("%d%m%Y%H"))
    days_remaining_delta = election_day - today
    days_remaining = days_remaining_delta.days
    if days_remaining < 1:
        days_remaining = 1
    big_future_uncertainty = np.log(days_remaining)*0.008 + days_remaining*0.00015
    small_future_uncertainty = np.log(days_remaining)*0.002 + days_remaining*0.0002
    print("BigStd: ",big_future_uncertainty+big_std)
    print("SmallStd: ",small_future_uncertainty+small_std)
    # 09032024 BigStd:  0.11802060145863788

    

    for i,p in enumerate(std_parties):
        if nat_polls[p] > 0.2:
            rng = np.random.default_rng(seed=base_seed+i)
            natchgs.append(rng.normal(chg_df[p],big_std+big_future_uncertainty,sims_num))
        else:
            rng = np.random.default_rng(seed=base_seed*2+i)
            natchgs.append(rng.normal(chg_df[p],small_std+small_future_uncertainty,sims_num))
    clusters = list(set(list(df["Cluster"])))
    for i,p in enumerate(std_parties):
        for c in clusters:
            if nat_polls[p] > 0.2:
                rng = np.random.default_rng(seed=base_seed*3+i)
                natchgs.append(rng.normal(0,big_std,sims_num))
            else:
                rng = np.random.default_rng(seed=base_seed*4+i)
                natchgs.append(rng.normal(0,small_std,sims_num))

    chg_dict = {}
    i=0
    for p in std_parties:
        chg_dict[p+"n"] = natchgs[i]
        i+=1
    for c in clusters:
        for p in std_parties:
            chg_dict[p+str(c)] = natchgs[i]
            i+=1
    rand_df = pd.DataFrame(chg_dict)

    # Create a dictionary to store the results for each constituency and party
    results = {}

    # Iterate over constituencies
    for con in constituencies:
        # Filter the dataframe for the current constituency
        con_df = df[df["New constituency name"] == con].copy()
        
        # Get the cluster, imputation uncertainty, and future uncertainty for the current constituency
        cluster = con_df["Cluster"].iloc[0]
        imputation_uncertainty = con_df["Low_Confidence_Imputation"].iloc[0]
        if cluster == 999:
            anomaly_uncertainty = 1
        else:
            anomaly_uncertainty = 0
        
        # Iterate over standard parties
        for i,p in enumerate(std_parties):
            # Get the previous results for the current party and constituency
            prev_res = con_df["2019_Results"+p+"_pc"]
            
            # Get the necessary data from the random dataframe
            nat_chg = rand_df[p+"n"]
            clr_chg = rand_df[p+str(cluster)]
            
            # Calculate the noise for the current constituency and party
            rng = np.random.default_rng(seed=base_seed*5+i)
            con_noise = [rng.normal(0, (1+imputation_uncertainty+anomaly_uncertainty)*small_std) for n in range(sims_num)]
            
            # Calculate the rough prediction for the current constituency and party
            prev_res_array = [float(prev_res.iloc[0]) for n in range(sims_num)]
            rough_pred = prev_res_array + nat_chg + clr_chg + con_noise
            rough_pred[rough_pred < 0] = 0
            
            # Store the results in the dictionary
            results[con+p+"Noise"] = con_noise
            results[con+p+"Rough"] = rough_pred
        
    # Update the random dataframe with the results
    rand_df = pd.concat([rand_df,pd.DataFrame(results)],axis=1)

    def get_winner(party_values, winner_val,parties = std_parties):
        for p,v in zip(parties,list(party_values)[0]):
            if v == winner_val:
                return p
    def get_margin(party_values):
        sorted_vals = sorted(list(party_values)[0])
        margin = sorted_vals[-1] - sorted_vals[-2]
        return margin

    final_dfs = [rand_df]
    for con in constituencies:
        con_cols = []
        for p in std_parties:
            con_cols.append(con+p+"Rough")
        final_df = rand_df[con_cols].copy()
        final_pred_cols = []
        for p in std_parties:
            final_df[con+p+"Final"] = final_df[con+p+"Rough"] / final_df[con_cols].sum(axis=1)
            final_pred_cols.append(con+p+"Final")
        final_df[con +"past_post_val"] = final_df[final_pred_cols].max(axis=1)
        final_df[con+"Margin"] = final_df[final_pred_cols].apply(lambda x:get_margin([x[final_pred_cols]]),axis=1)
        final_pred_cols.append(con +"past_post_val")
        final_df[con+"Winner"] = final_df[final_pred_cols].apply(lambda x:get_winner([x[final_pred_cols]],x[con+"past_post_val"]),axis=1)

                    
        # final_df[con+"Winner"] = winners
        final_dfs.append(final_df)
    rand_df = pd.concat(final_dfs, axis=1)

    seats_cols = []
    for p in std_parties:
        rand_df[p+"Seats"] = rand_df[[c + "Winner" for c in constituencies]].eq(p).sum(1)
        seats_cols.append(p+"Seats")

    max_seats = rand_df[seats_cols].max(1)
    results = []
    for n in range(sims_num):
        for col in seats_cols:
            if max_seats[n] ==rand_df[col].loc[n]:
                for p in std_parties:
                    if p + "Seats" == col:
                        winning_party = p
        
        if max_seats[n] <326:
            result = "Hung Parliament: Largest Party " + winning_party
        else:
            result = winning_party
        results.append(result)
    rand_df["Result"] = results

    winner_cols = [con+"Winner" for con in constituencies]
    winner_wins = []
    for col in winner_cols:
        winner_wins.append(max(list(rand_df[col].value_counts())))
    close_cols = []
    for col,wins in zip(winner_cols,winner_wins):
        if wins < 525:
            close_cols.append(col)
    all_final_cols = [con+p+"Final"for p in std_parties for con in constituencies]
    all_margin_cols = [con+"Margin"for p in std_parties for con in constituencies]
    winner_cols
    results_cols = ["Result"]
    all_result_cols = []
    for l in [all_final_cols,all_margin_cols,winner_cols,seats_cols,results_cols]:
        all_result_cols.extend(l)
    # results_df = rand_df[all_result_cols].transpose().copy()



    # rand_df.transpose().to_csv(output_path+str(today)+".csv")
    rand_df[all_result_cols].transpose().to_csv(output_path+str(today)+".csv")

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

def get_results_percentages(df):
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

def get_std_errors():
    poll_avgs = get_poll_avgs()
    pc_results = get_results_percentages()
    bigerrs = []
    for p,r in zip(poll_avgs,pc_results):
        conerr = float(p["con"] - r["con"])
        laberr = float(p["lab"] - r["lab"])

        bigerrs.append(conerr)
        bigerrs.append(laberr)
    big_std = np.std(bigerrs) * 1.1
    serrs = []
    for p,r in zip(poll_avgs,pc_results):
        liberr = float(p["lib"] - r["lib"])
        serrs.append(liberr)
        if "ref" in pd.DataFrame(p).transpose().columns:
            referr = float(p["ref"] - r["ref"])
            serrs.append(referr)
            
        if "nat" in pd.DataFrame(p).transpose().columns:
            naterr = float(p["nat"] - r["nat"])
            serrs.append(naterr)
    small_std = np.std(serrs) *1.1
    return big_std, small_std

def get_constituencies(res_path = "UKGE/outputs/resultsclusteredconstituencies.csv"):
    df = pd.read_csv(res_path)
    constituencies = list(df["New constituency name"])
    return constituencies

def today_results_exist(export_path="UKGE/outputs/EXPORT.csv"):
    export = pd.read_csv(export_path)
    today = datetime.date.today()
    return str(today) in export.columns

def get_descriptive_cluster_labels():
    return {
        0:"Labour",
        1:"Brexit",
        2:"Marginal",
        3:"SNP",
        4:"Brexit Conservative",
        5:"Conservative",
        6:"Immigrant",
        7:"Lib-Con",
        8:"Remain",
        9:"Nat-Conservative",
        999:"Anomalous"
    }

def get_descriptive_cluster_labels_17():
    return {
        0:"Old NW England",
        1:"Brexit Lab-Con Marginals",
        2:"SNP",
        3:"Labour Families",
        4:"Working Families",
        5:"Old Lib-Con SW",
        6:"Old Conservative",
        7:"Working Remain Lib-Cons SE",
        8:"Remain Working London",
        9:"Labour Brexit",
        999:"Anomalous"
    }