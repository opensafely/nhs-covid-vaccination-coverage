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

# # OpenSAFELY COVID Vaccine coverage report: Booster / third doses 

# OpenSAFELY is a new secure analytics platform for electronic patient records built on behalf of NHS England to deliver urgent academic and operational research during the pandemic. 
#
# This is an extension of our [regular weekly report](https://reports.opensafely.org/reports/vaccine-coverage/) on COVID-19 vaccination coverage in England using data from 40% of general practices that use TPP electronic health record software. **The data requires careful interpretation and there are a number of caveats. Please read the full detail about our methods and discussion of our earlier results (as of January 13th) in our preprint paper available [here](https://www.medrxiv.org/content/10.1101/2021.01.25.21250356v2).** 
#
# The full analytical methods behind the latest results in this report are available [here](https://github.com/opensafely/nhs-covid-vaccination-uptake).

# ## Booster/Third doses

# This report is intended to highlight any differences between subgroups of priority cohorts in receiving "booster" doses (or third primary doses where eligible), at least 6 months (27 weeks) after their second dose.

# +
from datetime import datetime
# %matplotlib inline
# %config InlineBackend.figure_format='png'

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
    display(Markdown(f"### Third dose vaccinations included up to **{latest_date_fmt}** inclusive"))
    
with open(os.path.join("..", "interim-outputs","text", "latest_date_of_second_dose_for_due_third_doses.txt"), 'r') as file:
    latest_date_27w_fmt = file.read()
    
display(Markdown(
    f"### Only persons who had their second dose at least 27 weeks ago (**{latest_date_27w_fmt}**) are included in the 'due' group."))


# -

# ##  
# ## Contents
#
# **Cumulative third dose vaccination figures among:**
# - [**80+** population](#Cumulative-second-dose-vaccination-figures-among-80+-population)
# - [**70-79** population](#Cumulative-second-dose-vaccination-figures-among-70-79-population)
# - [**Care home** population](#Cumulative-second-dose-vaccination-figures-among-care-home-population)
# - <a href="#Cumulative-second-dose-vaccination-figures-among-shielding-(aged-16-69)-population"><strong>Shielding (aged 16-69)</strong> population</a>
# - [**65-69** population](#Cumulative-second-dose-vaccination-figures-among-65-69-population)
# - <a href="#Cumulative-second-dose-vaccination-figures-among-Learning-Disabilities-(aged-16-64)-population"><strong>LD (aged 16-64)</strong> population</a>
# - [**60-64** population](#Cumulative-second-dose-vaccination-figures-among-60-64-population)
# - [**55-59** population](#Cumulative-second-dose-vaccination-figures-among-54-59-population)
# - [**50-54** population](#Cumulative-second-dose-vaccination-figures-among-50-54-population)
#
# The above links will become functional as each of the stated populations are included in the report. 
# - [**All groups (Summary**](#Summary))
#
#
#
#

with open('../lib/group_definitions.txt') as f:
    group_defs = f.read()
    display(Markdown(group_defs))

# +
tablelist = find_and_sort_filenames("tables", by_demographics_or_population="population", 
                                    pre_string="among ", tail_string=" population.csv",
                                    population_subset="Cumulative second dose 27w ago",
                                    files_to_exclude=["Cumulative second dose 27w ago vaccination figures among 16-17 population.csv"],
                                    )
    
# get 3rd dose figures for each group
tablelist_2nd = find_and_sort_filenames("tables", by_demographics_or_population="population", 
                                        pre_string="among ", tail_string=" population.csv",
                                        population_subset="Cumulative third dose vaccination",
                                        files_to_exclude=["Cumulative third dose vaccination figures among 16-17 population.csv"],
                                        )


second_third_doses(tablelist, tablelist_2nd, cohorts=["80+","70-79","care home", "shielding (aged 16-69)", "65-69"], dose_type="Third", time_period="27 weeks",
                   max_ylim=100,
                   latest_date_fmt=latest_date_fmt,
                   latest_date_fmt_2=latest_date_27w_fmt, 
                   backend=backend, suffix = "_tpp")

