"Module for data quality checks"

import os
from IPython.display import display, Markdown
import pandas as pd

# import custom functions from 'lib' folder
import sys
sys.path.append('../lib/')
from report_results import create_output_dirs, round7

def ethnicity_completeness(df, groups_of_interest):

    '''
    Describe completeness of ethnicity coding for group of interest
    
    Inputs:
    df (dataframe): processed patient-level dataframe containing "ethnicity_6_groups" column,
                    as well as "group"&""group_name" (to identify vaccine priority group) and "patient_id" (for counting)
    groups_of_interest (dict): dict mapping names of population/eligible subgroups to integers (1-9, and 0 for "other")
    
    Outputs:
    displays string describing n and % of given group with ethnicity known
    
    '''
    # create copy of df only with cols of interest
    cols = ["group", "group_name", "ethnicity_6_groups","patient_id"]   
    
    ethnicity_coverage = pd.DataFrame(columns=["group", "n with ethnicity", "total population (n)", "ethnicity coverage (%)"])
    
    
    for i, (groupname, groupno) in enumerate(groups_of_interest.items()):
        out = df[cols].copy()
        # filter dataframe to eligible group
        out = out.loc[(out["group_name"]==groupname)]
        
        total = round7(out["patient_id"].nunique())

        known_eth = out.groupby("ethnicity_6_groups")[["patient_id"]].nunique().reset_index()
        known_eth = known_eth.loc[known_eth["ethnicity_6_groups"]!="Unknown"]["patient_id"].sum()
        known_eth = round7(known_eth)
        percent = round(100*(known_eth/total), 1)
        
        # export ethnicity coverage stats to text file
        savepath, _, _ = create_output_dirs()
        
        ethnicity_coverage.loc[i] = [groupname, known_eth, total, percent]
        ethnicity_coverage.to_csv(os.path.join(savepath["text"], "ethnicity_coverage.csv"), index=False)
        

        display(Markdown(f"Total **{groupname}** population with ethnicity recorded {known_eth:,d} ({percent}%)"))
        

    
    
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
        