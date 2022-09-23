#!/usr/bin/env python
# coding: utf-8

# 
# # OpenSAFELY COVID Vaccine coverage report: first doses for 5 to 15 year olds
# 
# OpenSAFELY is a new secure analytics platform for electronic patient records built on behalf of NHS England to deliver urgent academic and operational research during the pandemic. 
# 
# Since December 2020 we have been reporting on COVID-19 vaccination coverage (for patients aged 16 and over) in England using data from 40% of general practices that use TPP electronic health record software. In [September 2021](https://www.england.nhs.uk/2021/09/nhs-rolls-out-covid-19-jab-to-children-aged-12-to-15/), the COVID vaccination programme was extended to 12-15 year olds. The [Living with Covid guidance](https://www.gov.uk/government/publications/covid-19-response-living-with-covid-19) was updated in February 2022 to advise that vaccines would be offered to children between the ages of 5 and 11 from Spring 2022. As such, we are now regularly reporting on vaccination coverage for children between the age of 5 and 15. 
# 
# **The data requires careful interpretation and there are a number of caveats, please refer to our peer-reviewed publications (https://doi.org/10.3399/BJGP.2021.0376) for further details. While this publication describes an analysis of vaccine uptake in those 16 and over, it is relevant here as the core functionality has been repurposed to generate our vaccine coverage reports for 5-15 year olds.**
# 
# The full analytical methods behind the latest results in this report are available [here](https://github.com/opensafely/nhs-covid-vaccination-uptake). 

# In[ ]:


from datetime import datetime
from IPython.display import display, Markdown
import os
import pandas as pd

pd.set_option("display.max_rows", 200)

group_string = "u16"
suffix = f"_{group_string}_tpp"


# ## Vaccines approved for use in children
# 
# The 30 microgram dose of the Pfizer BioNTech COVID-19 vaccine BNT162b2 was approved for use in 12-15 year olds in June 2021. In December 2021, the MHRA approved a 10 microgram dose for children aged 5-11 years.  Where the paediatric formulation is not available, 10 micrograms (0.1ml) of the diluted adult vaccine may be used as an alternative. The Moderna vaccine has also been approved for use in 12-17 year olds.
# 
# More information regarding vaccines approved for use is available in [The Green Book, chapter 14a](https://www.gov.uk/government/publications/covid-19-the-green-book-chapter-14a), see specifically the "Vaccine Effectiveness" (p.6-7) and "Dosing and Schedule" (p. 12-13) sections.

# #### 
# ## Contents
# - **<a href=#summary>Overview of all vaccination figures to date </a>**
# <br>
# <br>
# - **<a href=#brands>Brand counts (first dose)</a>**
# <br>
# <br>
# - **<a href=#summarychart>Summary charts (first dose)</a>**
# <br>
# <br>
# - **Charts:** Trends in first dose vaccination coverage according to demographic/clinical features, for:
#  - <a href=#5-11-population>5-11 population</a>
#  - <a href=#12-15-population>12-15 population</a>
# <br>
# <br>
# - **Tables:** Current first dose vaccination coverage according to demographic/clinical features, for:
#   - <a href=#Cumulative-vaccination-figures-among-5-11-population>5-11 population</a>
#   - <a href=#Cumulative-vaccination-figures-among-12-15-population>12-15 population</a> 
# <br>
# <br>
# - **Appendix:** <a href=#ethnicity>Proportion of each population group for whom ethnicity is known</a>
# 

# In[ ]:


with open(
    os.path.join("..", "interim-outputs", group_string, "text", "latest_date.txt"), "r"
) as file:
    latest_date_fmt = file.read()
    display(
        Markdown(f"### Vaccinations included up to **{latest_date_fmt}** inclusive")
    )


# In[ ]:


display(
    Markdown(f"### Report last updated **{datetime.today().strftime('%d %b %Y')}**")
)


# 
# ## Overview of Vaccination Figures to date <a name='summary' />

# In[ ]:


import json

summary_stats_1 = pd.read_csv(
    os.path.join(
        "..", "interim-outputs", group_string, "text", "summary_stats_first_dose.txt"
    )
).set_index("Unnamed: 0")
summary_stats_2 = pd.read_csv(
    os.path.join(
        "..", "interim-outputs", group_string, "text", "summary_stats_second_dose.txt"
    )
).set_index("Unnamed: 0")
additional_stats = pd.read_csv(
    os.path.join(
        "..", "interim-outputs", group_string, "text", "additional_stats_first_dose.txt"
    )
).set_index("Unnamed: 0")
group_brand_counts = pd.read_csv(
    os.path.join(
        "..", "interim-outputs", group_string, "text", "summary_stats_brand_counts.txt"
    )
).set_index(["Group", "Vaccine brand"])
group_brand_counts = group_brand_counts[["first_doses", "first_doses_perc"]]


# In[ ]:


# first display group definitions/caveats
with open(f"../lib/group_definitions_{group_string}.txt") as f:
    group_defs = f.read()
    display(Markdown(f"{group_defs} \n \n #### \n"))

# display summary table
out = summary_stats_1.join(summary_stats_2)
# out = out.join(summary_stats_3)
out.index = out.index.str.replace(f' in {suffix.replace("_","").upper()}', "")
out.index = out.index.rename("Group")
display(out)


# In[ ]:


display(
    Markdown(
        f"##### \n"
        "**Notes**\n"
        "\n- Patient counts are rounded to nearest 7\n"
        "\n- Second doses are at least 49 days after the first\n"
        "\n- All second doses given in these timescales are counted whether or not they were 'due' according to the relevant dosing schedule at the time\n"
    )
)

display(Markdown("##### \n"))


# ## Brand counts <a name='brands' />

# Note that the total in this table may not be identical to that provided elsewhere
# and percentages may not sum to 100%. There are several aspects of the recorded data
# and analysis that impact on these totals:
# 
# * It is not always possible to determine the vaccine type given; these patients are removed from the brand totals
# * Occasionally patients have more than one brand recorded on the same day; these patients are removed from the brand totals
# * We round to seven to mitigate against risk of disclosure; these totals are calculated from previously rounded numbers 

# In[ ]:


brand_summary = group_brand_counts.rename(
    columns={
        "first_doses": f"First doses as at {latest_date_fmt}",
        "first_doses_perc": f"% first doses as at {latest_date_fmt}",
    }
)

display(brand_summary)


# In[ ]:


display(
    Markdown(
        f"##### \n"
        "**Notes**\n"
        "\n- Patient counts are rounded to nearest 7\n"
        "\n- 'Other' vaccines are Oxford-AZ or Moderna\n"
    )
)

display(Markdown("##### \n"))


# # 
# 
# ## Summary Charts <a name='summarychart' />

# In[ ]:


import sys

sys.path.append("../lib/")
from create_report import *
from image_formats import pick_image_format

IMAGE_FORMAT = pick_image_format()

show_chart(
    f"Cumulative first dose vaccination figures by risk status.{IMAGE_FORMAT.extension}",
    IMAGE_FORMAT,
    org_breakdown=group_string,
    title="off",
)

display(
    Markdown(
        "**Note:** The 'In a risk group' includes those identified as being at higher risk of severe COVID-19 (for details see the <a href='#Group-definitions'>Group Definitions</a> section)."
    )
)

show_chart(
    f"Cumulative first dose vaccination figures by age group.{IMAGE_FORMAT.extension}",
    IMAGE_FORMAT,
    org_breakdown=group_string,
    title="off",
)


#  
# <!-- EXAMPLE PRIORITY GROUP BREAKDOWN ------------
# ## Trends in vaccination rates of **80+** population according to demographic/clinical features, cumulatively by day. <a name='charts80' />
# **\*_Latest overall cohort rate_ calculated as at latest date for vaccinations recorded across all TPP practices.**
# ------------------------------------------------->

# In[ ]:


display(Markdown("## 5-11 population"))

chartlist1 = find_and_sort_filenames(
    foldername="figures",
    org_breakdown="u16",
    population_subset="5-11",
    file_extension=IMAGE_FORMAT.extension,
    files_to_exclude=[
        f"Cumulative plot of time to second dose among 5-11 population by all.{IMAGE_FORMAT.extension}"
    ],
)

for item in chartlist1:
    show_chart(item, IMAGE_FORMAT, org_breakdown="u16")


# In[ ]:


display(Markdown("## 12-15 population"))

chartlist2 = find_and_sort_filenames(
    foldername="figures",
    org_breakdown="u16",
    population_subset="12-15",
    file_extension=IMAGE_FORMAT.extension,
    files_to_exclude=[
        f"Cumulative plot of time to second dose among 12-15 population by all.{IMAGE_FORMAT.extension}"
    ],
)

for item in chartlist2:
    show_chart(item, IMAGE_FORMAT, org_breakdown="u16")


# # 
# ## Vaccination rates of each eligible population group, according to demographic/clinical features  <a name='tables' />
#   - <a href=#Cumulative-vaccination-figures-among-5-11-population>5-11</a>  population
#   - <a href=#Cumulative-vaccination-figures-among-12-15-population>12-15</a>  population
# <br>

# In[ ]:


tablelist = find_and_sort_filenames(
    "tables",
    by_demographics_or_population="population",
    org_breakdown=group_string,
    pre_string="among ",
    tail_string=" population.csv",
    population_subset="Cumulative vaccination figures",
    files_to_exclude=[],
)


# In[ ]:


for filename in tablelist:
    df, title = import_table(
        filename,
        latest_date_fmt,
        show_carehomes=True,
        org_breakdown=group_string,
        suffix=suffix,
    )

    ### Can't embed this in the f string below due to curly brackets
    date_string = latest_date_fmt.replace(" 202\d{1}", "")

    column_list = [f"Vaccinated at {date_string} (n)", f"Total eligible"]

    show_table(
        df, title, latest_date_fmt, count_columns=column_list, show_carehomes=True
    )


# ### 
# ## Appendix 
# ### <a id='ethnicity'> Ethnicity coverage for each eligible group </a>
# 
# The table below shows the proportion of each population group for whom ethnicity is known.

# In[ ]:


from create_report import get_savepath

savepath = get_savepath(subfolder=group_string)
tab = pd.read_csv(os.path.join(savepath["text"], "ethnicity_coverage.csv")).set_index(
    "group"
)
# tab.index = tab.index.str.replace("vaccinated 18-29", "18-29")
display(
    Markdown(
        "- Ethnicity information is primarily retrieved from GP records. \
                 \n- Where missing in GP records, as of March 8 2021, it is then retrieved from hospital records if present. \
                 \n - For patients with multiple different ethnicities recorded, we use the most common non-missing ethnicity \
                 \n recorded in inpatients, outpatients or A&E over the last ~5 years (or latest if tied).\
                 \n- Patient counts are rounded to the nearest 7"
    )
)

tab[["total population (n)", "ethnicity coverage (%)"]]

