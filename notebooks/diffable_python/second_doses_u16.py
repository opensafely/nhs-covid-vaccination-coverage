#!/usr/bin/env python
# coding: utf-8

# # OpenSAFELY COVID Vaccine coverage report: second doses for 5 to 15 year olds
# 
# OpenSAFELY is a new secure analytics platform for electronic patient records built on behalf of NHS England to deliver urgent academic and operational research during the pandemic. 
# 
# Since December 2020 we have been reporting on COVID-19 vaccination coverage (for patients aged 16 and over) in England using data from 40% of general practices that use TPP electronic health record software. In [September 2021](https://www.england.nhs.uk/2021/09/nhs-rolls-out-covid-19-jab-to-children-aged-12-to-15/), the COVID vaccination programme was extended to 12-15 year olds. The [Living with Covid guidance](https://www.gov.uk/government/publications/covid-19-response-living-with-covid-19) was updated in February 2022 to advise that vaccines would be offered to children between the ages of 5 and 11 from Spring 2022. As such, we are now regularly reporting on vaccination coverage for children between the age of 5 and 15. 
# 
# **The data requires careful interpretation and there are a number of caveats, please refer to our peer-reviewed publications (https://doi.org/10.3399/BJGP.2021.0376) for further details. While this publication describes an analysis of vaccine uptake in those 16 and over, it is relevant here as the core functionality has been repurposed to generate our vaccine coverage reports for 5-15 year olds.**
# 
# The full analytical methods behind the latest results in this report are available [here](https://github.com/opensafely/nhs-covid-vaccination-uptake). 

# In[ ]:



import json
import sys
import pandas as pd
import os
from IPython.display import display, Markdown
from datetime import datetime
get_ipython().run_line_magic('matplotlib', 'inline')
get_ipython().run_line_magic('config', "InlineBackend.figure_format = 'png'")

pd.set_option("display.max_rows", 200)
sys.path.append('../lib/')

from second_third_doses import *
from create_report import find_and_sort_filenames

backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
group_string = "u16"
suffix = f"_{group_string}_tpp"


# ## Vaccines approved for use in children
# 
# The 30 microgram dose of the Pfizer BioNTech COVID-19 vaccine BNT162b2 was approved for use in 12-15 year olds in June 2021. In December 2021, the MHRA approved a 10 microgram dose for children aged 5-11 years.  Where the paediatric formulation is not available, 10 micrograms (0.1ml) of the diluted adult vaccine may be used as an alternative. The Moderna vaccine has also been approved for use in 12-17 year olds.
# 
# More information regarding vaccines approved for use is available in [The Green Book, chapter 14a](https://www.gov.uk/government/publications/covid-19-the-green-book-chapter-14a), see specifically the "Vaccine Effectiveness" (p.6-7) and "Dosing and Schedule" (p. 12-13) sections.

# ## Second doses

# Second doses are recommended to occur within 8 weeks for children at high risk and within 12 weeks for all other children. In this report we consider an individual to be 'due' to receive their second dose if their first dose more than 14 weeks ago. Anyone who as *not* had their second dose by 14 weeks is described as 'overdue'.
# 
# **Please note**: This report is intended to highlight any differences between population subgroups in receiving second doses, only including those which are due (i.e. where at least 14 weeks has passed since the first dose) unless otherwise stated. **It is therefore NOT a comprehensive view of all second doses given to date** - to see these figures please refer to the main report.

# In[ ]:




display(Markdown(f"### Report last updated **{datetime.today().strftime('%d %b %Y')}**"))

with open(os.path.join("..", "interim-outputs",group_string,"text", "latest_date.txt"), 'r') as file:
    latest_date_fmt = file.read()
    display(Markdown(f"### Second dose vaccinations included up to **{latest_date_fmt}** inclusive"))
    
with open(os.path.join("..", "interim-outputs",group_string,"text", "latest_date_of_first_dose_for_due_second_doses.txt"), 'r') as file:
    latest_date_secondDUE_fmt = file.read()
    
display(Markdown(
    f"### Only 5-15 year olds who had their first dose between the start of the campaign (**4th August 2021**) \
    and 7 weeks ago (**{latest_date_secondDUE_fmt}**) are included in the 'due' group."))

additional_stats = pd.read_csv(os.path.join("..", "interim-outputs", group_string,"text", "additional_stats_first_dose.txt")).set_index("Unnamed: 0")

group_brand_counts = pd.read_csv(os.path.join("..", "interim-outputs", group_string,"text", "summary_stats_brand_counts.txt")).set_index(["Group","Vaccine brand"])
group_brand_counts = group_brand_counts[["second_doses", "second_doses_perc"]]


# #### 
# ## Contents
# - **<a href=#brands>Brand counts (second dose)</a>**
# <br>
# <br>
# - **Tables:** Current second dose vaccination coverage according to demographic/clinical features, for:
#   - <a href=#Cumulative-second-dose-vaccination-figures-among-5-11-population>5-11 population</a>
#   - <a href=#Cumulative-second-dose-vaccination-figures-among-12-15-population>12-15 population</a>
# <br>
# <br>
# - **Table:** <a href="#Summary"> Summary of second dose vaccination coverage </a>
# <br>
# 

# In[ ]:


with open(f'../lib/group_definitions_{group_string}.txt') as f:
    group_defs = f.read()
    display(Markdown(group_defs))


# ## Brand counts <a name='brands' />

# Note that the total in this table may not be identical to that provided elsewhere
# and percentages may not sum to 100%. There are several aspects of the recorded data
# and analysis that impact on these totals:
# 
# * It is not always possible to determine the vaccine type given; these patients are removed from the brand totals
# * Occasionally patients have more than one brand recorded on the same day; these patients are removed from the brand totals
# * We round to seven to mitigate against risk of disclosure; these totals are calculated from previously rounded numbers
# * Second doses are counted here whether they are 'due' or not 

# In[ ]:


brand_summary = group_brand_counts.rename(
    columns={"second_doses":f"Second doses as at {latest_date_fmt}",
            "second_doses_perc":f"% second doses as at {latest_date_fmt}" }
    )

display( brand_summary )


# In[ ]:


display(Markdown(f"##### \n" 
                 "**Notes**\n"
                 "\n- Patient counts are rounded to nearest 7\n"
                 "\n- 'Other' vaccines are Oxford-AZ or Moderna\n"
                 "\n- For the brand totals, second doses given in these timescales are counted whether or not they were 'due' according to the relevant dosing schedule at the time." ))

display(Markdown("##### \n"))


# In[ ]:



display(Markdown(f"### Second dose coverage by first dose brand\n\n"
                 f"The percentage of second doses received by first dose brand are provided below.\n\n"
                 f"Note that these figures are raw proportions and do not take into account how many are due; this may vary substantially by brand.\n\n"))

display(Markdown("##### \n"))

for x in additional_stats.index[3:]:
    display(Markdown(f"{x}: {additional_stats.loc[x][0]}\n"))

display(Markdown("##### \n"))

### Mixed doses not calculated as yet.
# display(Markdown("<br>**Note:** mixed doses counts patients with first and second doses at least 49 days apart, \
#                   excluding patients with two different brands recorded on the same day \
#                   or recorded on a date prior to when the given brand was available in the UK"))

# for x in additional_stats.index[7:]:
#     display(Markdown(f"{x}: {additional_stats.loc[x][0]}\n"))


# In[ ]:


tablelist = find_and_sort_filenames("tables", by_demographics_or_population="population_reversed", 
                                    org_breakdown=group_string,
                                    pre_string="among ", tail_string=" population.csv",
                                    population_subset="Cumulative first dose 14w ago",
                                    # files_to_exclude=["Cumulative first dose 14w ago vaccination figures among 5-11 population.csv"],
                                    )
    
# get 2nd dose figures for each group
tablelist_2nd = find_and_sort_filenames("tables", by_demographics_or_population="population_reversed", 
                                        org_breakdown=group_string,
                                        pre_string="among ", tail_string=" population.csv",
                                        population_subset="Cumulative second dose vaccination",
                                        # files_to_exclude=["Cumulative second dose vaccination figures among 5-11 population.csv"],
                                        )


# In[ ]:



second_third_doses(tablelist, tablelist_2nd, dose_type="Second", time_period="14 weeks",
                   org_breakdown=group_string,
                   latest_date_fmt=latest_date_fmt,
                   latest_date_fmt_2=latest_date_secondDUE_fmt,
                   max_ylim=100,
                   backend=backend, suffix = suffix)
   

