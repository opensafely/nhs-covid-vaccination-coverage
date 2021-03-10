"Module for data quality checks"

import os
from IPython.display import display, Markdown
import pandas as pd

# import custom functions from 'lib' folder
import sys
sys.path.append('../lib/')
from report_results import create_output_dirs, filter_other_group, round7

def ethnicity_completeness(df, groups_of_interest):

    '''
    Describe completeness of ethnicity coding for group of interest
    
    Inputs:
    df (dataframe): processed patient-level dataframe containing "ethnicity_6_groups" column,
                    as well as "community_ageband" (for filtering to given group) and "patient_id" (for counting)
    group (str): group of interest e.g. "80+"
    name_of_other_group (str): name to give for the general population who are vaccinated but do not have recorded eligibility factors
    groups_not_in_other_group (list): groups to exclude from "other" group, i.e. all currently included criteria for eligibility
    
    Outputs:
    displays string describing n and % of given group with ethnicity known
    
    '''
    # create copy of df only with cols of interest
    cols = [v for v in set(groups_of_interest.values()) if v != "other"]
    cols.extend(["ethnicity_6_groups","patient_id"])   
        
    ethnicity_coverage = pd.DataFrame(columns=["group", "n with ethnicity", "total population (n)", "ethnicity coverage (%)"])
    
    for i, (group_title, group_label) in enumerate(groups_of_interest.items()):
        out = df[cols].copy()
        # filter dataframe to eligible group
        if group_label == "other": # for "all others" filter out the each of the defined groups
            # we want to exclude all the other eligible groups from the "other" group
            out = filter_other_group(out, groups_of_interest=groups_of_interest)
        elif group_label != "community_ageband": # for groups not defined as age bands or care home, filter out care home population
            out = out.loc[(out["community_ageband"]!="care home") & (out[group_label]==group_title)]
        # will need a further filter for the "clinically vulnerable" group here
        else:    # age groups / care home
            out = out.loc[(out[group_label]==group_title)]

        total = round7(out["patient_id"].nunique())

        known_eth = out.groupby("ethnicity_6_groups")[["patient_id"]].nunique().reset_index()
        known_eth = known_eth.loc[known_eth["ethnicity_6_groups"]!="Unknown"]["patient_id"].sum()
        known_eth = round7(known_eth)
        percent = round(100*(known_eth/total), 1)
        
        # export ethnicity coverage stats to text file
        savepath, _, _ = create_output_dirs()
        ethnicity_coverage.loc[i] = [group_title, known_eth, total, percent]
        ethnicity_coverage.to_csv(os.path.join(savepath["text"], "ethnicity_coverage.csv"), index=False)
        

        display(Markdown(f"Total **{group_title}** population with ethnicity recorded {known_eth:,d} ({percent}%)"))
        

    
    
def care_home_flag_comparison(df):
    '''
    Compare number of patients flagged with each different care home flag
    
    Inputs:
    df (dataframe): processed patient-level dataframe
    
    Outputs:
    display text describing care home population according to each flag
    '''
    
    df = df[["care_home_primis","care_home","patient_id","ageband"]].copy().loc[(df["care_home_primis"]==1)|(df["care_home"]=="yes")].loc[df["ageband"].isin(["65-69","60-69","70-79","80+"])]
    out = df.groupby(["care_home_primis","care_home"])[["patient_id"]].nunique().unstack().fillna(0).astype(int)
    out = out.to_numpy()
    out_dict={}
    out_dict["address flag"]=out[0][1]
    out_dict["snomed flag"]=out[1][0]
    out_dict["both"]=out[1][1]
    total = sum(out_dict.values())
    display(Markdown("#### Care home flags"))
    for p, v in out_dict.items():
        percent = 100*round(v/total, 3)
        display(Markdown(f"Patients with {p} = {v} ({percent}%)"))
        