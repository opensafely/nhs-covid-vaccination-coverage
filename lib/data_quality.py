"Module for data quality checks"

from IPython.display import display, Markdown
import pandas as pd


def ethnicity_completeness(df, group, 
                           name_of_other_group="all other vaccinated people, not in eligible groups shown",
                           groups_not_in_other_group=["care home","80+", "70-79"]):

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
    # group without denominator
    if group == "other":
        out = df[["community_ageband","ethnicity_6_groups","patient_id"]].copy()
        out = out.loc[~out["community_ageband"].isin(groups_not_in_other_group)]        
        group = name_of_other_group
        
    # in subgroups with denominators
    else:
        out = df[["community_ageband","ethnicity_6_groups","patient_id"]].copy()
        out = out.loc[out["community_ageband"]==group]

    total = out["patient_id"].nunique()

    known_eth = out.groupby("ethnicity_6_groups")[["patient_id"]].nunique().reset_index()
    known_eth = known_eth.loc[known_eth["ethnicity_6_groups"]!="Unknown"]["patient_id"].sum()
        
    percent = round(100*(known_eth/total), 1)
        
    
    display(Markdown(f"Total **{group}** population with ethnicity recorded {known_eth:,d} ({percent}%)"))

    
    
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
        