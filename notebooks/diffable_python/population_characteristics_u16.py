#!/usr/bin/env python
# coding: utf-8

# In[ ]:



# # Vaccines and patient characteristics


# In[ ]:







# ### Import libraries and data
# 
# The datasets used for this report are created using the study definition [`/analysis/study_definition.py`](../analysis/study_definition.py), using codelists referenced in [`/codelists/codelists.txt`](../codelists/codelists.txt). 


# In[ ]:




get_ipython().run_line_magic('load_ext', 'autoreload')
get_ipython().run_line_magic('autoreload', '2')

import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import subprocess
from IPython.display import display, Markdown, HTML
import os
import copy

group_string = "u16"
suffix = f"_{group_string}_tpp"

# get current branch
current_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True).stdout.decode("utf8").strip()


# ### Import our custom functions


# In[ ]:




# import custom functions from 'lib' folder
import sys
sys.path.append('../lib/')


# In[ ]:




from data_processing import load_child_data
from second_third_doses import abbreviate_time_period


# In[ ]:




from report_results import find_and_save_latest_date, create_output_dirs, report_results, round7


# In[ ]:




# create output directories to save files into 
savepath, savepath_figure_csvs, savepath_table_csvs = create_output_dirs(subfolder=group_string)


# ### Load and Process the raw data 


# In[ ]:


df = load_child_data( input_file=f'input_delivery_{group_string}.csv.gz', save_path = savepath )


# In[ ]:




latest_date, formatted_latest_date = find_and_save_latest_date(df, savepath=savepath)


# In[ ]:




print(f"Latest Date: {formatted_latest_date}")


# ### Summarise by group and demographics at latest date

# #### Calculate cumulative sums at each date and select latest date + previous figures for comparison


# In[ ]:




from report_results import cumulative_sums


# In[ ]:




# population subgroups - in a dict to indicate which field to filter on


population_subgroups = {"5-11": 1,
                        "12-15": 2,
        # NB if the population denominator is not included for the final group (0), the key must contain phrase "not in other eligible groups" so that data is presented appropriately
        }

groups = population_subgroups.keys()


#  list demographic/clinical factors to include for given group
DEFAULT = ["sex", "ethnicity_6_groups", "ethnicity_16_groups", "imd_categories"]

# dictionary mapping population subgroups to a list of demographic/clinical factors to include for that group
features_dict = {0:    DEFAULT, ## patients not assigned to a priority group
                 "5-11": DEFAULT,
                 "12-15": DEFAULT,
                 "DEFAULT": DEFAULT # other age groups
                }


# In[ ]:


df_dict_cum = cumulative_sums(df, groups_of_interest=population_subgroups, features_dict=features_dict, latest_date=latest_date, all_keys=[0,1,2])


# In[ ]:



# for details on second/third doses, no need for breakdowns of any groups (only "overall" figures will be included)
second_dose_features = {}
for g in groups:
    second_dose_features[g] = []

df_dict_cum_second_dose = cumulative_sums(df, groups_of_interest=population_subgroups, features_dict=second_dose_features,
                                          latest_date=latest_date, reference_column_name="covid_vacc_second_dose_date")

# df_dict_cum_third_dose = cumulative_sums(df, groups_of_interest=population_subgroups, features_dict=second_dose_features, 
#                                           latest_date=latest_date, reference_column_name="covid_vacc_third_dose_date")

# ### Cumulative vaccination figures - overall


# In[ ]:




from report_results import make_vaccine_graphs


# In[ ]:




make_vaccine_graphs(df, latest_date=latest_date, grouping="priority_status", savepath_figure_csvs=savepath_figure_csvs, savepath=savepath, suffix=suffix)


# In[ ]:




make_vaccine_graphs(df, latest_date=latest_date, include_total=False, savepath=savepath, savepath_figure_csvs=savepath_figure_csvs, suffix=suffix)


# ### Reports 


# In[ ]:




from report_results import summarise_data_by_group


# In[ ]:




summarised_data_dict = summarise_data_by_group(df_dict_cum, latest_date=latest_date, groups=groups)


# In[ ]:




summarised_data_dict_2nd_dose = summarise_data_by_group(df_dict_cum_second_dose, latest_date=latest_date, groups=groups)

# summarised_data_dict_3rd_dose = summarise_data_by_group(df_dict_cum_third_dose, latest_date=latest_date, groups=groups)


# ### Proportion of each eligible population vaccinated to date


# In[ ]:




from report_results import create_summary_stats_children, create_detailed_summary_uptake


# In[ ]:




summ_stat_results, additional_stats, group_brand_counts = create_summary_stats_children(df, summarised_data_dict, formatted_latest_date, groups=groups, 
                                         savepath=savepath, suffix=suffix)


# In[ ]:




summ_stat_results_2nd_dose, _, _ = create_summary_stats_children(df, summarised_data_dict_2nd_dose, formatted_latest_date, 
                                                  groups=groups, savepath=savepath, 
                                                  vaccine_type="second_dose", suffix=suffix)

# summ_stat_results_3rd_dose, _, _ = create_summary_stats_children(df, summarised_data_dict_3rd_dose, formatted_latest_date, 
#                                                    groups=groups, savepath=savepath, 
#                                                    vaccine_type="third_dose", suffix=suffix)


# In[ ]:




# display the results of the summary stats on first and second doses
display(pd.DataFrame(summ_stat_results).join(pd.DataFrame(summ_stat_results_2nd_dose)))#.join(pd.DataFrame(summ_stat_results_3rd_dose)))
display(Markdown(f"*\n figures rounded to nearest 7"))


# In[ ]:




# other information on vaccines

for x in additional_stats.keys():
    display(Markdown(f"{x}: {additional_stats[x]}"))
    
display(Markdown(f"*\n figures rounded to nearest 7"))


# # Detailed summary of coverage among population groups as at latest date


# In[ ]:




create_detailed_summary_uptake(summarised_data_dict, formatted_latest_date, 
                               groups=population_subgroups.keys(),
                               savepath=savepath)


# # Demographics time trend charts


# In[ ]:




from report_results import plot_dem_charts


# In[ ]:




plot_dem_charts(summ_stat_results, df_dict_cum,  formatted_latest_date,
                pop_subgroups=["5-11","12-15"],
                groups_dict=features_dict,
                # groups_to_exclude=["ethnicity_16_groups", "current_copd", "chronic_cardiac_disease", "dmards", "chemo_or_radio", "lung_cancer", "cancer_excl_lung_and_haem", "haematological_cancer"],
                savepath=savepath, savepath_figure_csvs=savepath_figure_csvs, suffix=suffix)


# ## Completeness of ethnicity recording


# In[ ]:




from data_quality import *

ethnicity_completeness(df=df, groups_of_interest=population_subgroups, savepath=savepath )


# # Second doses


# In[ ]:




# only count second doses where the first dose was given at least 14 weeks ago 
# to allow comparison of the first dose situation secondDue ago with the second dose situation now
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
    with open(os.path.join(savepath["text"], f"{description}_specified_delay.txt"), "w") as text_file:
        formatted_delay = f"{number} {unit}"
        text_file.write(formatted_delay)

    display(Markdown(formatted_date))
    return new_date, formatted_date
    

second_scheduling = 14
second_scheduling_string_short = f"{second_scheduling}w"
second_scheduling_string_long = f"{second_scheduling} weeks"

date_secondDue, formatted_date_secondDue = subtract_from_date(s=df["covid_vacc_date"], unit="weeks", number=second_scheduling,
                                             description="latest_date_of_first_dose_for_due_second_doses")


# In[ ]:




# filter data
df_s = df.copy()
# replace any second doses not yet "due" with "0"
df_s.loc[(pd.to_datetime(df_s["covid_vacc_date"]) >= date_secondDue), "covid_vacc_second_dose_date"] = 0

# also ensure that first dose was dated after the start of the campaign, otherwise date is likely incorrect 
# and due date for second dose cannot be calculated accurately
# this also excludes any second doses where first dose date = 0 (this should affect dummy data only!)
df_s.loc[(pd.to_datetime(df_s["covid_vacc_date"]) <= "2021-08-04"), "covid_vacc_second_dose_date"] = 0


# In[ ]:




# add "brand of first dose" to list of features to break down by
features_dict_2 = copy.deepcopy(features_dict)

for k in features_dict_2:
    ls = list(features_dict_2[k])
    ls.append("brand_of_first_dose") 
    features_dict_2[k] = ls


# In[ ]:




# data processing / summarising
df_dict_cum_second_dose = cumulative_sums(df_s, groups_of_interest=population_subgroups, features_dict=features_dict_2, 
                                          latest_date=latest_date, reference_column_name="covid_vacc_second_dose_date")

second_dose_summarised_data_dict = summarise_data_by_group(df_dict_cum_second_dose, latest_date=latest_date, groups=groups)

create_detailed_summary_uptake(second_dose_summarised_data_dict, formatted_latest_date, 
                               groups=groups,
                               savepath=savepath, vaccine_type="second_dose")


# In[ ]:



second_dose_summarised_data_dict = summarise_data_by_group(df_dict_cum_second_dose, latest_date=latest_date, groups=groups)

create_detailed_summary_uptake(second_dose_summarised_data_dict, formatted_latest_date, 
                               groups=groups,
                               savepath=savepath, vaccine_type="second_dose")

## For comparison look at first doses UP TO 14 WEEKS AGO


# In[ ]:




# latest date of 14 weeks ago is entered as the latest_date when calculating cumulative sums below.

# Seperately, we also ensure that first dose was dated after the start of the campaign, 
# to be consistent with the second doses due calculated above
df_secondDue = df.copy()
df_secondDue.loc[(pd.to_datetime(df_secondDue["covid_vacc_date"]) <= "2021-08-04"), "covid_vacc_date"] = 0


df_dict_cum_secondDue = cumulative_sums(
                                  df_secondDue, groups_of_interest=population_subgroups, features_dict=features_dict_2, 
                                  latest_date=date_secondDue
                                  )

summarised_data_dict_secondDue = summarise_data_by_group(
                                                   df_dict_cum_secondDue, 
                                                   latest_date=date_secondDue, 
                                                   groups=groups
                                                   )

create_detailed_summary_uptake(summarised_data_dict_secondDue, formatted_latest_date=date_secondDue, 
                               groups=groups,
                               savepath=savepath, vaccine_type=f"first_dose_{second_scheduling_string_short}_ago")


# # Booster/third doses


# In[ ]:




# Only want to count third doses where the second dose was given some period of time ago.
# This period of time is defined by the variables booster_delay_number and booster_delay_unit.

# booster_delay_number = 14
# booster_delay_unit = "weeks"
# booster_delay_unit_short = abbreviate_time_period( booster_delay_unit )

# date_3rdDUE, formatted_date_3rdDUE = subtract_from_date(s=df["covid_vacc_date"], unit=booster_delay_unit, number=booster_delay_number,
#                                                         description="latest_date_of_second_dose_for_due_third_doses")


# In[ ]:




# # filtering for third doses that are "due"

# df_t = df.copy()
# # replace any third doses not yet "due" with "0"
# df_t.loc[(pd.to_datetime(df_t["covid_vacc_second_dose_date"]) >= date_3rdDUE), "covid_vacc_third_dose_date"] = 0

# # also ensure that second dose was dated (2weeks) after the start of the campaign, otherwise date is likely incorrect 
# # and due date for third dose cannot be calculated accurately
# # this also excludes any third doses where second dose date = 0 (this should affect dummy data only!)
# df_t.loc[(pd.to_datetime(df_t["covid_vacc_second_dose_date"]) <= "2021-09-22"), "covid_vacc_third_dose_date"] = 0


# In[ ]:




# # summarise third doses to date (after filtering above)

# # Include 18+ age groups plus priority groups (50+/CEV/Care home etc) only
# population_subgroups_third = {key: value for key, value in population_subgroups.items() if 0 < value < 13}

# df_dict_cum_third_dose = cumulative_sums(df_t, groups_of_interest=population_subgroups_third, features_dict=features_dict,
#                                          latest_date=latest_date, reference_column_name="covid_vacc_third_dose_date")

# third_dose_summarised_data_dict = summarise_data_by_group(
#     df_dict_cum_third_dose, latest_date=latest_date, groups=population_subgroups_third.keys())

# create_detailed_summary_uptake(third_dose_summarised_data_dict, formatted_latest_date,
#                                groups=population_subgroups_third.keys(),
#                                savepath=savepath, vaccine_type="third_dose")


# In[ ]:




# display(Markdown(f"## For comparison look at second dose coverate UP TO {booster_delay_number} {booster_delay_unit.upper()} AGO"))


# In[ ]:




# # latest date of 200 days ago is entered as the latest_date when calculating cumulative sums below.

# # Seperately, we also ensure that second dose was dated 2 weeks after the start of the campaign, 
# # to be consistent with the third doses due calculated above
# df_3rdDUE = df.copy()
# df_3rdDUE.loc[(pd.to_datetime(df_3rdDUE["covid_vacc_second_dose_date"]) <= "2021-09-22"), "covid_vacc_second_dose_date"] = 0

# df_dict_cum_3rdDUE = cumulative_sums(
#     df_3rdDUE, groups_of_interest=population_subgroups_third, features_dict=features_dict,
#     latest_date=date_3rdDUE,
#                                   reference_column_name="covid_vacc_second_dose_date"
#                                   )

# summarised_data_dict_3rdDUE = summarise_data_by_group(
#                                                    df_dict_cum_3rdDUE, latest_date=date_3rdDUE,
#                                                    groups=population_subgroups_third.keys()
#                                                    )

# create_detailed_summary_uptake(summarised_data_dict_3rdDUE, formatted_latest_date=date_3rdDUE,
#                                groups=population_subgroups_third.keys(),
#                                savepath=savepath, vaccine_type=f"second_dose_{booster_delay_number}{booster_delay_unit_short}_ago")


# In[ ]:




# df_dict_cum_3rdDUE = cumulative_sums(
#     df_3rdDUE, groups_of_interest=population_subgroups_third, features_dict=features_dict,
#     latest_date=date_3rdDUE,
#                                   reference_column_name="covid_vacc_second_dose_date"
#                                   )

# summarised_data_dict_3rdDUE = summarise_data_by_group(
#                                                    df_dict_cum_3rdDUE, latest_date=date_3rdDUE,
#                                                    groups=population_subgroups_third.keys()
#                                                    )

# create_detailed_summary_uptake(summarised_data_dict_3rdDUE, formatted_latest_date=date_3rdDUE,
#                                groups=population_subgroups_third.keys(),
#                                savepath=savepath, vaccine_type=f"second_dose_{booster_delay_number}{booster_delay_unit_short}_ago")

