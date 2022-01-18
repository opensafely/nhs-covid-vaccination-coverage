#!/usr/bin/env python
# coding: utf-8

# # OpenSAFELY COVID Vaccine coverage report: Second doses 

# OpenSAFELY is a new secure analytics platform for electronic patient records built on behalf of NHS England to deliver urgent academic and operational research during the pandemic. 
# 
# This is an extension of our [regular weekly report](https://reports.opensafely.org/reports/vaccine-coverage/) on COVID-19 vaccination coverage in England using data from 40% of general practices that use TPP electronic health record software. **The data requires careful interpretation and there are a number of caveats. Please read the full detail about our methods and discussion of our earlier results (as of 17 March 2021) in our paper available [here](https://doi.org/10.3399/BJGP.2021.0376).** 
# 
# The full analytical methods behind the latest results in this report are available [here](https://github.com/opensafely/nhs-covid-vaccination-uptake).
# 
# **Update: As of 17th January 2022, our vaccine reports will be published fortnightly.  If you rely on weekly data updates for your own reporting or analysis please contact team@opensafely.org to let us know.**

# ## Second doses

# **Please note** This report is intended to highlight any differences between subgroups of priority cohorts in receiving second doses, only including those which are due (i.e. where at least 14 weeks has passed since the first dose). **It is therefore NOT a comprehensive view of all second doses given to date** - to see these figures please refer to the main report. 

# In[1]:


from datetime import datetime
get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('config', "InlineBackend.figure_format='png'")

from IPython.display import display, Markdown
import os
import pandas as pd
pd.set_option("display.max_rows", 200)
import sys
sys.path.append('../lib/')
from create_report import find_and_sort_filenames
from second_third_doses import *

backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
suffix = "_tpp"

display(Markdown(f"### Report last updated **{datetime.today().strftime('%d %b %Y')}**"))

with open(os.path.join("..", "interim-outputs","text", "latest_date.txt"), 'r') as file:
    latest_date_fmt = file.read()
    display(Markdown(f"### Second dose vaccinations included up to **{latest_date_fmt}** inclusive"))
    
with open(os.path.join("..", "interim-outputs","text", "latest_date_of_first_dose_for_due_second_doses.txt"), 'r') as file:
    latest_date_14w_fmt = file.read()
    
display(Markdown(
    f"### Only persons who had their first dose between the start of the campaign (**7 Dec 2020**) \
    and 14 weeks ago (**{latest_date_14w_fmt}**) are included in the 'due' group."))


# ##  
# ## Contents
# 
# **Cumulative second dose vaccination figures among:**
# - [**80+** population](#Cumulative-second-dose-vaccination-figures-among-80+-population)
# - [**70-79** population](#Cumulative-second-dose-vaccination-figures-among-70-79-population)
# - [**Care home** population](#Cumulative-second-dose-vaccination-figures-among-care-home-population)
# - <a href="#Cumulative-second-dose-vaccination-figures-among-shielding-(aged-16-69)-population"><strong>Shielding (aged 16-69)</strong> population</a>
# - [**65-69** population](#Cumulative-second-dose-vaccination-figures-among-65-69-population)
# - <a href="#Cumulative-second-dose-vaccination-figures-among-Learning-Disabilities-(aged-16-64)-population"><strong>LD (aged 16-64)</strong> population</a>
# - [**60-64** population](#Cumulative-second-dose-vaccination-figures-among-60-64-population)
# - [**55-59** population](#Cumulative-second-dose-vaccination-figures-among-55-59-population)
# - [**50-54** population](#Cumulative-second-dose-vaccination-figures-among-50-54-population)
# - [**40-49** population](#Cumulative-second-dose-vaccination-figures-among-40-49-population)
# - [**30-39** population](#Cumulative-second-dose-vaccination-figures-among-30-39-population)
# - [**18-29** population](#Cumulative-second-dose-vaccination-figures-among-18-29-population)
# 
# [**SUMMARY**](#Summary)
# 

# In[2]:


with open('../lib/group_definitions.txt') as f:
    group_defs = f.read()
    display(Markdown(group_defs))


# In[3]:


tablelist = find_and_sort_filenames("tables", by_demographics_or_population="population", 
                                    pre_string="among ", tail_string=" population.csv",
                                    population_subset="Cumulative first dose 14w ago",
                                    files_to_exclude=["Cumulative first dose 14w ago vaccination figures among 16-17 population.csv"],
                                    )
    
# get 2nd dose figures for each group
tablelist_2nd = find_and_sort_filenames("tables", by_demographics_or_population="population", 
                                        pre_string="among ", tail_string=" population.csv",
                                        population_subset="Cumulative second dose vaccination",
                                        files_to_exclude=["Cumulative second dose vaccination figures among 16-17 population.csv"],
                                        )


second_third_doses(tablelist, tablelist_2nd, dose_type="Second", time_period="14 weeks",
                   latest_date_fmt=latest_date_fmt,
                   latest_date_fmt_2=latest_date_14w_fmt, 
                   backend=backend, suffix = "_tpp")
   

