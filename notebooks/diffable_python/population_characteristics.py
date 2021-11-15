# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: all
#     notebook_metadata_filter: all,-language_info
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.3.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# + [markdown]
# # Vaccines and patient characteristics
# -


# ### Import libraries and data
#
# The datasets used for this report are created using the study definition [`/analysis/study_definition.py`](../analysis/study_definition.py), using codelists referenced in [`/codelists/codelists.txt`](../codelists/codelists.txt). 

# +
# %load_ext autoreload
# %autoreload 2
 
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import subprocess
from IPython.display import display, Markdown, HTML
import os

suffix = "_tpp"

# get current branch
current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True).stdout.decode("utf8").strip()
# -

# ### Import our custom functions

# import custom functions from 'lib' folder
import sys
sys.path.append('../lib/')

from data_processing import load_data

from report_results import find_and_save_latest_date, create_output_dirs

# create output directories to save files into 
savepath, savepath_figure_csvs, savepath_table_csvs = create_output_dirs()

# ### Load and Process the raw data 

df = load_data()

latest_date, formatted_latest_date = find_and_save_latest_date(df, savepath=savepath)

print(f"Latest Date: {formatted_latest_date}")

# ### Summarise by group and demographics at latest date

# #### Calculate cumulative sums at each date and select latest date + previous figures for comparison

from report_results import cumulative_sums

# +
# population subgroups - in a dict to indicate which field to filter on


population_subgroups = {"80+":1,
        "70-79":2, 
        "care home":3, 
        "shielding (aged 16-69)":4, 
        "65-69": 5,  
        "LD (aged 16-64)": 6,  
        "60-64": 7,
        "55-59": 8,
        "50-54": 9,
        "40-49": 10,
        "30-39": 11,
        "18-29": 12,                
        "16-17": 0 
        # NB if the population denominator is not included for the final group (0), the key must contain phrase "not in other eligible groups" so that data is presented appropriately
        }

groups = population_subgroups.keys()


#  list demographic/clinical factors to include for given group
DEFAULT = ["sex","ageband_5yr","ethnicity_6_groups","ethnicity_16_groups", "imd_categories", 
                              "bmi", "housebound", "chronic_cardiac_disease", "current_copd", "dialysis", "dmards", "dementia",
                              "psychosis_schiz_bipolar","LD","ssri",
                              "chemo_or_radio", "lung_cancer", "cancer_excl_lung_and_haem", "haematological_cancer"]
#for specific age bands remove features which are included elsehwere or not prevalent
o65 = [d for d in DEFAULT if d not in ("ageband_5yr", "dialysis")]
o60 = [d for d in DEFAULT if d not in ("ageband_5yr", "dialysis", "LD", "housebound")]
o50 = [d for d in DEFAULT if d not in ("ageband_5yr", "dialysis", "LD", "dementia",
                                       "chemo_or_radio", "lung_cancer", "cancer_excl_lung_and_haem", "haematological_cancer", "housebound"
                                      )]
# under50s
u50 = ["sex", "ethnicity_6_groups", "ethnicity_16_groups","imd_categories"]

# dictionary mapping population subgroups to a list of demographic/clinical factors to include for that group
features_dict = {0:    u50, ## patients not assigned to a priority group
                 "care home": ["sex", "ageband_5yr", "ethnicity_6_groups", "dementia"],
                 "shielding (aged 16-69)": ["newly_shielded_since_feb_15", "sex", "ageband", "ethnicity_6_groups", "imd_categories",
                                           "LD"],
                 "65-69":    o65,
                 "60-64":    o60,
                 "55-59":    o50,
                 "50-54":    o50,
                 "40-49":    u50,
                 "30-39":    u50,
                 "18-29":    u50,
                 "16-17":    ["sex", "ethnicity_6_groups", "imd_categories"],
                 "LD (aged 16-64)":  ["sex", "ageband_5yr", "ethnicity_6_groups"],
                 "DEFAULT":   DEFAULT # other age groups
                }

# -


df_dict_cum = cumulative_sums(df, groups_of_interest=population_subgroups, features_dict=features_dict, latest_date=latest_date)

# +
# for details on second/third doses, no need for breakdowns of any groups (only "overall" figures will be included)
second_dose_features = {}
for g in groups:
    second_dose_features[g] = []

df_dict_cum_second_dose = cumulative_sums(df, groups_of_interest=population_subgroups, features_dict=second_dose_features, 
                                          latest_date=latest_date, reference_column_name="covid_vacc_second_dose_date")

df_dict_cum_third_dose = cumulative_sums(df, groups_of_interest=population_subgroups, features_dict=second_dose_features, 
                                          latest_date=latest_date, reference_column_name="covid_vacc_third_dose_date")
# -

# ### Cumulative vaccination figures - overall

from report_results import make_vaccine_graphs

make_vaccine_graphs(df, latest_date=latest_date, grouping="priority_status", savepath_figure_csvs=savepath_figure_csvs, savepath=savepath, suffix=suffix)

make_vaccine_graphs(df, latest_date=latest_date, include_total=False, savepath=savepath, savepath_figure_csvs=savepath_figure_csvs, suffix=suffix)

# ### Reports 

from report_results import summarise_data_by_group

summarised_data_dict = summarise_data_by_group(df_dict_cum, latest_date=latest_date, groups=groups)

# +
summarised_data_dict_2nd_dose = summarise_data_by_group(df_dict_cum_second_dose, latest_date=latest_date, groups=groups)

summarised_data_dict_3rd_dose = summarise_data_by_group(df_dict_cum_third_dose, latest_date=latest_date, groups=groups)
# -

# ### Proportion of each eligible population vaccinated to date

from report_results import create_summary_stats, create_detailed_summary_uptake

summ_stat_results, additional_stats = create_summary_stats(df, summarised_data_dict, formatted_latest_date, groups=groups, 
                                         savepath=savepath, suffix=suffix)

# +
summ_stat_results_2nd_dose, _ = create_summary_stats(df, summarised_data_dict_2nd_dose, formatted_latest_date, 
                                                  groups=groups, savepath=savepath, 
                                                  vaccine_type="second_dose", suffix=suffix)

summ_stat_results_3rd_dose, _ = create_summary_stats(df, summarised_data_dict_3rd_dose, formatted_latest_date, 
                                                  groups=groups, savepath=savepath, 
                                                  vaccine_type="third_dose", suffix=suffix)
# -

# display the results of the summary stats on first and second doses
display(pd.DataFrame(summ_stat_results).join(pd.DataFrame(summ_stat_results_2nd_dose)).join(pd.DataFrame(summ_stat_results_3rd_dose)))   
display(Markdown(f"*\n figures rounded to nearest 7"))

# +
# other information on vaccines

for x in additional_stats.keys():
    display(Markdown(f"{x}: {additional_stats[x]}"))
    
display(Markdown(f"*\n figures rounded to nearest 7"))
# -

# # Detailed summary of coverage among population groups as at latest date

create_detailed_summary_uptake(summarised_data_dict, formatted_latest_date, 
                               groups=population_subgroups.keys(),
                               savepath=savepath)

# # Demographics time trend charts

from report_results import plot_dem_charts

plot_dem_charts(summ_stat_results, df_dict_cum,  formatted_latest_date, pop_subgroups=["80+", "70-79", "65-69","shielding (aged 16-69)", "60-64", "55-59", "50-54", "40-49", "30-39", "18-29"], groups_dict=features_dict,
                groups_to_exclude=["ethnicity_16_groups", "current_copd", "chronic_cardiac_disease", "dmards", "chemo_or_radio", "lung_cancer", "cancer_excl_lung_and_haem", "haematological_cancer"],
                savepath=savepath, savepath_figure_csvs=savepath_figure_csvs, suffix=suffix)

# ## Completeness of ethnicity recording

# +
from data_quality import *

ethnicity_completeness(df=df, groups_of_interest=population_subgroups)

# -

# # Second doses

# +
# only count second doses where the first dose was given at least 14 weeks ago 
# to allow comparison of the first dose situation 14w ago with the second dose situation now
# otherwise bias could be introduced from any second doses given early in certain subgroups

def subtract_from_date(s, unit, number, description):
    '''
    s (series): a series of date-like strings
    unit (str) : days/weeks
    number (int): number of days/weeks to subtract
    description (str): description of new date calculated to use as filename
    '''
    if unit == "weeks":
        new_date = pd.to_datetime(s).max() - timedelta(weeks=number)
    elif unit == "days":
        new_date = pd.to_datetime(s).max() - timedelta(days=number)
    else:
        display("invalid unit")
        return
    new_date = str(new_date)[:10]

    formatted_date = datetime.strptime(new_date, "%Y-%m-%d").strftime("%d %b %Y")
    with open(os.path.join(savepath["text"], f"{description}.txt"), "w") as text_file:
            text_file.write(formatted_date)
    
    display(Markdown(formatted_date))
    return new_date, formatted_date    
    

date_14w, formatted_date_14w = subtract_from_date(s=df["covid_vacc_date"], unit="weeks", number=14, 
                                             description="latest_date_of_first_dose_for_due_second_doses")

# +
# filter data
df_s = df.copy()
# replace any second doses not yet "due" with "0"
df_s.loc[(pd.to_datetime(df_s["covid_vacc_date"]) >= date_14w), "covid_vacc_second_dose_date"] = 0

# also ensure that first dose was dated after the start of the campaign, otherwise date is likely incorrect 
# and due date for second dose cannot be calculated accurately
# this also excludes any second doses where first dose date = 0 (this should affect dummy data only!)
df_s.loc[(pd.to_datetime(df_s["covid_vacc_date"]) <= "2020-12-07"), "covid_vacc_second_dose_date"] = 0


# +
# add "brand of first dose" to list of features to break down by
import copy
features_dict_2 = copy.deepcopy(features_dict)

for k in features_dict_2:
    ls = list(features_dict_2[k])
    ls.append("brand_of_first_dose") 
    features_dict_2[k] = ls

# +
# data processing / summarising
df_dict_cum_second_dose = cumulative_sums(df_s, groups_of_interest=population_subgroups, features_dict=features_dict_2, 
                                          latest_date=latest_date, reference_column_name="covid_vacc_second_dose_date")

second_dose_summarised_data_dict = summarise_data_by_group(df_dict_cum_second_dose, latest_date=latest_date, groups=groups)

create_detailed_summary_uptake(second_dose_summarised_data_dict, formatted_latest_date, 
                               groups=groups,
                               savepath=savepath, vaccine_type="second_dose")

# ## For comparison look at first doses UP TO 14 WEEKS AGO
#

# +
# latest date of 14 weeks ago is entered as the latest_date when calculating cumulative sums below.

# Seperately, we also ensure that first dose was dated after the start of the campaign, 
# to be consistent with the second doses due calculated above
df_14w = df.copy()
df_14w.loc[(pd.to_datetime(df_14w["covid_vacc_date"]) <= "2020-12-07"), "covid_vacc_date"] = 0


df_dict_cum_14w = cumulative_sums(
                                  df_14w, groups_of_interest=population_subgroups, features_dict=features_dict_2, 
                                  latest_date=date_14w
                                  )

summarised_data_dict_14w = summarise_data_by_group(
                                                   df_dict_cum_14w, 
                                                   latest_date=date_14w, 
                                                   groups=groups
                                                   )

create_detailed_summary_uptake(summarised_data_dict_14w, formatted_latest_date=date_14w, 
                               groups=groups,
                               savepath=savepath, vaccine_type="first_dose_14w_ago")
# -

# # Booster/third doses

# +
# only want to count third doses where the second dose was given a little over 6 months ago (26 weeks+1)
# here we use latest date of any first dose just to calculate the date 27w ago. 

date_27w, formatted_date_27w = subtract_from_date(s=df["covid_vacc_date"], unit="weeks", number=27, 
                                             description="latest_date_of_second_dose_for_due_third_doses")

# +
# filtering for third doses that are "due"

df_t = df.copy()
# replace any third doses not yet "due" with "0"
df_t.loc[(pd.to_datetime(df_t["covid_vacc_second_dose_date"]) >= date_27w), "covid_vacc_third_dose_date"] = 0

# also ensure that second dose was dated (2weeks) after the start of the campaign, otherwise date is likely incorrect 
# and due date for third dose cannot be calculated accurately
# this also excludes any third doses where second dose date = 0 (this should affect dummy data only!)
df_t.loc[(pd.to_datetime(df_t["covid_vacc_second_dose_date"]) <= "2020-12-21"), "covid_vacc_third_dose_date"] = 0


# +
# summarise third doses to date (after filtering above)

# keep priority groups (50+/CEV/Care home etc) only
population_subgroups_third = {key:value for key,value in population_subgroups.items() if 0 < value < 10}

df_dict_cum_third_dose = cumulative_sums(df_t, groups_of_interest=population_subgroups_third, features_dict=features_dict, 
                                          latest_date=latest_date, reference_column_name="covid_vacc_third_dose_date")

third_dose_summarised_data_dict = summarise_data_by_group(df_dict_cum_third_dose, latest_date=latest_date, groups=population_subgroups_third.keys())

create_detailed_summary_uptake(third_dose_summarised_data_dict, formatted_latest_date, 
                               groups=population_subgroups_third.keys(),
                               savepath=savepath, vaccine_type="third_dose")
# -

# ## For comparison look at second dose coverage UP TO 27 WEEKS AGO
#

# +
# latest date of 200 days ago is entered as the latest_date when calculating cumulative sums below.

# Seperately, we also ensure that second dose was dated 2 weeks after the start of the campaign, 
# to be consistent with the third doses due calculated above
df_27w = df.copy()
df_27w.loc[(pd.to_datetime(df_27w["covid_vacc_second_dose_date"]) <= "2020-12-21"), "covid_vacc_second_dose_date"] = 0



df_dict_cum_27w = cumulative_sums(
                                  df_27w, groups_of_interest=population_subgroups_third, features_dict=features_dict, 
                                  latest_date=date_27w, 
                                  reference_column_name="covid_vacc_second_dose_date"
                                  )

summarised_data_dict_27w = summarise_data_by_group(
                                                   df_dict_cum_27w, 
                                                   latest_date=date_27w, 
                                                   groups=population_subgroups_third.keys()
                                                   )

create_detailed_summary_uptake(summarised_data_dict_27w, formatted_latest_date=date_27w, 
                               groups=population_subgroups_third.keys(),
                               savepath=savepath, vaccine_type="second_dose_27w_ago")
