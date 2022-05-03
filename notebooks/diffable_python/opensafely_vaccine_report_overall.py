#!/usr/bin/env python
# coding: utf-8

# # OpenSAFELY COVID Vaccine coverage report
# 
# OpenSAFELY is a new secure analytics platform for electronic patient records built on behalf of NHS England to deliver urgent academic and operational research during the pandemic. 
# 
# This is our regular weekly report on COVID-19 vaccination coverage in England using data from 40% of general practices that use TPP electronic health record software. **The data requires careful interpretation and there are a number of caveats. Please read the full detail about our methods and discussion of our earlier results (as of 17 March 2021) in our [peer-reviewed publication in the British Journal of General Practice](https://doi.org/10.3399/BJGP.2021.0376).** 
# 
# The full analytical methods behind the latest results in this report are available [here](https://github.com/opensafely/nhs-covid-vaccination-uptake).
# 
# **Update: As of 17th January 2022, our vaccine reports will be published fortnightly.  If you rely on weekly data updates for your own reporting or analysis please contact team@opensafely.org to let us know.**

# In[ ]:


from datetime import datetime
from IPython.display import display, Markdown
import os
import pandas as pd
pd.set_option("display.max_rows", 200)

suffix = "_tpp"

display(Markdown(f"### Report last updated **{datetime.today().strftime('%d %b %Y')}**"))

with open(os.path.join("..", "interim-outputs","text", "latest_date.txt"), 'r') as file:
    latest_date_fmt = file.read()
    display(Markdown(f"### Vaccinations included up to **{latest_date_fmt}** inclusive"))

with open(os.path.join("..", "interim-outputs","text", "latest_date_of_first_dose_for_due_second_doses.txt"), 'r') as file:
    latest_date_13w_fmt = file.read()


# #### 
# ## Contents:
# - **<a href=#summary>Overview</a>**   (NEW: now includes third/booster dose counts)
# <br>
# <br>
# - **<a href=#summarychart>Summary Charts</a>**
# <br>
# <br>
# - **Charts:** Trends in first dose vaccination coverage according to demographic/clinical features, for:
#  - <a href=#charts80>80+ population</a>
#  - <a href=#charts70>70-79 population</a>
#  - <a href=#charts_shield>shielding (aged 16-69) population</a>
#  - <a href=#charts65>65-69 population</a>
#  - <a href=#charts60>60-64 population</a>
#  - <a href=#charts55>55-59 population</a>
#  - <a href=#charts50>50-54 population</a>
#  - <a href=#charts40>40-49 population</a>
# <br>
# <br>
# - **Tables:** Current first dose vaccination coverage according to demographic/clinical features, for:
#   - <a href=#Cumulative-vaccination-figures-among-80+-population>80+</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-70-79-population>70-79</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-care-home-population>care home (65+)</a> population
#   - <a href=#Cumulative-vaccination-figures-among-shielding-(aged-16-69)-population>shielding (aged 16-69)</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-65-69-population>65-69</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-Learning-Disabilities-(aged-16-64)-population>LD (aged 16-64)</a> populations.
#   - <a href=#Cumulative-vaccination-figures-among-60-64-population>60-64</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-55-59-population>55-59</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-50-54-population>50-54</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-40-49-population>40-49</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-30-39-population>30-39</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-18-29-population>18-29</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-16-17-population>16-17</a>  population
# <br>
# <br>
# - Appendix: <a href=#ethnicity>Proportion of each population group for whom ethnicity is known</a>
# 

# 
# ## Overview of Vaccination Figures to date <a name='summary' />

# In[ ]:


import json
summary_stats_1 = pd.read_csv(os.path.join("..", "interim-outputs","text", "summary_stats_first_dose.txt")).set_index("Unnamed: 0")
summary_stats_2 = pd.read_csv(os.path.join("..", "interim-outputs","text", "summary_stats_second_dose.txt")).set_index("Unnamed: 0")
summary_stats_3 = pd.read_csv(os.path.join("..", "interim-outputs","text", "summary_stats_third_dose.txt")).set_index("Unnamed: 0")
additional_stats = pd.read_csv(os.path.join("..", "interim-outputs","text", "additional_stats_first_dose.txt")).set_index("Unnamed: 0")

# first display group definitions/caveats
with open('../lib/group_definitions.txt') as f:
    group_defs = f.read()
    display(Markdown(f"{group_defs} #### \n"))
    
# display summary table
out = summary_stats_1.join(summary_stats_2)
out = out.join(summary_stats_3)
out.index = out.index.rename("Group")
display(out)

display(Markdown(f"##### \n" 
                 "**NB** Patient counts are rounded to nearest 7\n"
                 "\nSecond doses are at least 19 days after the first; third doses at least 8 weeks after the second;\n"
                 "\nAll second and third/booster doses given in these timescales are counted whether or not they were 'due' according to the relevant dosing schedule at the time.\n"
                "##### \n" ))

display(Markdown(f"##### \n"
                 f"### Vaccine types\n"
                 f"**Note:** numbers may not sum to 100% as it is not always possible to determine vaccine type given, and patients occasionally have more than one brand recorded on the same day."))

for x in additional_stats.index[0:3]:  
    display(Markdown(f"{x}: {additional_stats.loc[x][0]}\n"))
    
display(Markdown(f"### Second doses and dose combinations" ))
display(Markdown("**Note:** second dose figures are raw proportions and do not take into account how many are due, which is likely to vary substantially by brand.<br>                For more detailed analysis please refer to our [second dose report](https://reports.opensafely.org/reports/vaccine-coverage-second-doses/)"))

for x in additional_stats.index[3:7]:  
    display(Markdown(f"{x}: {additional_stats.loc[x][0]}\n"))
    
display(Markdown("<br>**Note:** mixed doses counts patients with first and second doses at least 19 days apart,                   excluding patients with two different brands recorded on the same day                   or recorded on a date prior to when the given brand was available in the UK"))
       
for x in additional_stats.index[7:]:  
    display(Markdown(f"{x}: {additional_stats.loc[x][0]}\n"))

    


# # 
# 
# ## Summary Charts <a name='summarychart' />

# In[ ]:


import sys
sys.path.append('../lib/')
from create_report import *
from image_formats import pick_image_format

IMAGE_FORMAT = pick_image_format()

show_chart(f"Cumulative first dose vaccination figures by priority status.{IMAGE_FORMAT.extension}", IMAGE_FORMAT, title="off")
display(Markdown("**Note:** 'Priority groups' only includes those identified as being in a priority group by our methodology.                 'Others' includes everyone aged 18-49 except those who are shielding or have a learning disability.<br><br>"))
show_chart(f"Cumulative first dose vaccination figures by priority group.{IMAGE_FORMAT.extension}", IMAGE_FORMAT, title="off")


# # 
# ## Trends in vaccination rates of **80+** population according to demographic/clinical features, cumulatively by day. <a name='charts80' />
# **\*_Latest overall cohort rate_ calculated as at latest date for vaccinations recorded across all TPP practices.**

# In[ ]:


chartlist = find_and_sort_filenames(foldername="figures", file_extension=IMAGE_FORMAT.extension)
   
display(Markdown("## 80+ population"))
for item in chartlist:
    show_chart(item, IMAGE_FORMAT)


# # 
# ## Trends in vaccination rates of **70-79** population according to demographic/clinical features, cumulatively by day. <a name='charts70' />
# **\*National rate calculated as at latest date for vaccinations recorded across all TPP practices.**
#     

# In[ ]:


display(Markdown("## 70-79 population"))
chartlist2 = find_and_sort_filenames(foldername="figures", population_subset="70-79", file_extension=IMAGE_FORMAT.extension)
    
for item in chartlist2:
    show_chart(item, IMAGE_FORMAT)


# ## 
# ## Trends in vaccination rates of **shielding** population according to demographic/clinical features, cumulatively by day. <a name='charts_shield' />
# **\*National rate calculated as at latest date for vaccinations recorded across all TPP practices.**
# 

# In[ ]:


display(Markdown("## Shielding population (aged 16-69)"))
chartlist2 = find_and_sort_filenames(foldername="figures", population_subset="shielding (aged 16-69)", file_extension=IMAGE_FORMAT.extension)
    
for item in chartlist2:
    show_chart(item, IMAGE_FORMAT)


# ## 
# ## Trends in vaccination rates of 65-69 population according to demographic/clinical features, cumulatively by day. <a name='charts65' />
# **\*National rate calculated as at latest date for vaccinations recorded across all TPP practices.**

# In[ ]:


display(Markdown("## 65-69 population"))
chartlist2 = find_and_sort_filenames(foldername="figures", population_subset="65-69", file_extension=IMAGE_FORMAT.extension)
    
for item in chartlist2:
    show_chart(item, IMAGE_FORMAT)


# ## 
# ## Trends in vaccination rates of 60-64 population according to demographic/clinical features, cumulatively by day. <a name='charts60' />
# **\*National rate calculated as at latest date for vaccinations recorded across all TPP practices.**
# 

# In[ ]:


display(Markdown("## 60-64 population"))
chartlist2 = find_and_sort_filenames(foldername="figures", population_subset="60-64", file_extension=IMAGE_FORMAT.extension)
    
for item in chartlist2:
    show_chart(item, IMAGE_FORMAT)


# ## 
# ## Trends in vaccination rates of 55-59 population according to demographic/clinical features, cumulatively by day. <a name='charts55' />
# **\*National rate calculated as at latest date for vaccinations recorded across all TPP practices.**

# In[ ]:


display(Markdown("## 55-59 population"))
chartlist2 = find_and_sort_filenames(foldername="figures", population_subset="55-59", file_extension=IMAGE_FORMAT.extension)
    
for item in chartlist2:
    show_chart(item, IMAGE_FORMAT)


# ## 
# ## Trends in vaccination rates of 50-54 population according to demographic/clinical features, cumulatively by day. <a name='charts50' />
# **\*National rate calculated as at latest date for vaccinations recorded across all TPP practices.**
# 
# +

# In[ ]:


display(Markdown("## 50-54 population"))
chartlist2 = find_and_sort_filenames(foldername="figures", population_subset="50-54", file_extension=IMAGE_FORMAT.extension)
    
for item in chartlist2:
    show_chart(item, IMAGE_FORMAT)


# ## 
# ## Trends in vaccination rates of 40-49 population according to demographic/clinical features, cumulatively by day. <a name='charts40' />
# **\*National rate calculated as at latest date for vaccinations recorded across all TPP practices.**

# In[ ]:


display(Markdown("## 40-49 population"))
chartlist2 = find_and_sort_filenames(foldername="figures", population_subset="40-49", file_extension=IMAGE_FORMAT.extension)
    
for item in chartlist2:
    show_chart(item, IMAGE_FORMAT)


# # 
# ## Vaccination rates of each eligible population group, according to demographic/clinical features  <a name='tables' />
#   - <a href=#Cumulative-vaccination-figures-among-80+-population>80+</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-70-79-population>70-79</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-care-home-population>care home (65+)</a> population
#   - <a href=#Cumulative-vaccination-figures-among-shielding-(aged-16-69)-population>shielding (aged 16-69)</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-65-69-population>65-69</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-Learning-Disabilities-(aged-16-64)-population>LD (aged 16-64)</a> populations.
#   - <a href=#Cumulative-vaccination-figures-among-60-64-population>60-64</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-55-59-population>55-59</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-50-54-population>50-54</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-40-49-population>40-49</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-30-39-population>30-39</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-18-29-population>18-29</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-16-17-population>16-17</a>  population
# <br>

# In[ ]:


tablelist = find_and_sort_filenames("tables", by_demographics_or_population="population", 
                            pre_string="among ", tail_string=" population.csv",
                            population_subset="Cumulative vaccination figures",
                            files_to_exclude=[])
    
for filename in tablelist:
    df, title = import_table(filename, latest_date_fmt, show_carehomes=True, suffix=suffix)

    ### Can't embed this in the f string below due to curly brackets
    date_string = latest_date_fmt.replace(' 202\d{1}','')

    column_list = [
        f"Vaccinated at {date_string} (n)", 
        f"Total eligible"
    ]
            
    show_table(df, title, latest_date_fmt, count_columns=column_list, show_carehomes=True)


# ### 
# ## Appendix 
# ### Ethnicity coverage for each eligible group <a name='ethnicity' />

# In[ ]:


from create_report import get_savepath
savepath = get_savepath()
tab = pd.read_csv(os.path.join(savepath["text"], "ethnicity_coverage.csv")).set_index("group")
tab.index = tab.index.str.replace("vaccinated 18-29", "18-29")
display(Markdown("- Ethnicity information is primarily retrieved from GP records.                  \n- Where missing in GP records, as of March 8 2021, it is then retrieved from hospital records if present.                  \n - For patients with multiple different ethnicities recorded, we use the most common non-missing ethnicity                  \n recorded in inpatients, outpatients or A&E over the last ~5 years (or latest if tied).                 \n- Patient counts are rounded to the nearest 7"))

tab[["total population (n)","ethnicity coverage (%)"]]

