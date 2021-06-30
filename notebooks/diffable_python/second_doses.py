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

# # OpenSAFELY COVID Vaccine coverage report: Second doses 

# OpenSAFELY is a new secure analytics platform for electronic patient records built on behalf of NHS England to deliver urgent academic and operational research during the pandemic. 
#
# This is an extension of our [regular weekly report](https://reports.opensafely.org/reports/vaccine-coverage/) on COVID-19 vaccination coverage in England using data from 40% of general practices that use TPP electronic health record software. **The data requires careful interpretation and there are a number of caveats. Please read the full detail about our methods and discussion of our earlier results (as of January 13th) in our preprint paper available [here](https://www.medrxiv.org/content/10.1101/2021.01.25.21250356v2).** 
#
# The full analytical methods behind the latest results in this report are available [here](https://github.com/opensafely/nhs-covid-vaccination-uptake).

# ## Second doses

# **Please note** This report is intended to highlight any differences between subgroups of priority cohorts in receiving second doses, only including those which are due (i.e. where at least 14 weeks has passed since the first dose). **It is therefore NOT a comprehensive view of all second doses given to date** - to see these figures please refer to the main report. 

# +
from datetime import datetime
import matplotlib.pyplot as plt
# %matplotlib inline
# %config InlineBackend.figure_format='png'

from IPython.display import display, Markdown
import os
import pandas as pd
pd.set_option("display.max_rows", 200)
import sys
sys.path.append('../lib/')
from create_report import *

backend = os.getenv("OPENSAFELY_BACKEND", "expectations")
suffix = "_tpp"

display(Markdown(f"### Report last updated **{datetime.today().strftime('%d %b %Y')}**"))

with open(os.path.join("..", "interim-outputs","text", "latest_date.txt"), 'r') as file:
    latest_date_fmt = file.read()
    display(Markdown(f"### Second dose vaccinations included up to **{latest_date_fmt}** inclusive"))

with open(os.path.join("..", "interim-outputs","text", "latest_date_of_first_dose_for_due_second_doses.txt"), 'r') as file:
    latest_date_14w_fmt = file.read()
    
display(Markdown(
    f"### Only persons who had their first dose at least 14 weeks ago ({latest_date_14w_fmt}) are included in the 'due' group."))
# -

# ##  
# ## Contents
#
# **Cumulative second dose vaccination figures among:**
# - [**80+** population](#Cumulative-second-dose-vaccination-figures-among-80+-population)
# - [**70-79** population](#Cumulative-second-dose-vaccination-figures-among-70-79-population)
# - [**Care home** population](#Cumulative-second-dose-vaccination-figures-among-care-home-population)
# - [**Shielding (aged 16-69)** population](#Cumulative-second-dose-vaccination-figures-among-shielding-(aged-16-69\)-population)
# - [**65-69** population](#Cumulative-second-dose-vaccination-figures-among-65-69-population)
# - [**LD (aged 16-64)** population](#Cumulative-second-dose-vaccination-figures-among-LD-(aged-16-64\)-population)
# - [**60-64** population](#Cumulative-second-dose-vaccination-figures-among-60-64-population)
# - [**55-59** population](#Cumulative-second-dose-vaccination-figures-among-54-59-population)
# - [**50-54** population](#Cumulative-second-dose-vaccination-figures-among-50-54-population)
#
# The above groups are only included in the report once at least 70% of their total population are due second doses.

# +

tablelist = find_and_sort_filenames("tables", by_demographics_or_population="population", 
                                    pre_string="among ", tail_string=" population.csv",
                                    population_subset="Cumulative first dose 14w ago",
                                    files_to_exclude=["Cumulative first dose 14w ago vaccination figures among 16-64, not in other eligible groups shown population.csv"],
                                    )
    
# get 2nd dose figures for each group
tablelist_2nd = find_and_sort_filenames("tables", by_demographics_or_population="population", 
                                        pre_string="among ", tail_string=" population.csv",
                                        population_subset="Cumulative second dose vaccination",
                                        files_to_exclude=["Cumulative second dose vaccination figures among 16-64, not in other eligible groups shown population.cscv"],
                                        )


for f, f2 in zip(tablelist, tablelist_2nd):
    display(Markdown("[Back to top](#Contents)"))
    df, _ = import_table(f, latest_date_fmt=latest_date_14w_fmt, show_carehomes=True, suffix=suffix, export_csv=False)
    df = df.drop(["Previous week's vaccination coverage (%)", "Total eligible", "Vaccinated over last 7d (%)"],1)
    
    df2, title = import_table(f2, latest_date_fmt, show_carehomes=True, suffix=suffix, export_csv=False)
    df2 = df2.drop(["Previous week's vaccination coverage (%)", "Vaccinated over last 7d (%)"],1)
    
    # column renaming and number formatting
    for c in df2.columns:
        if "(n)" in c:
            df2[c] = pd.to_numeric(df2[c], downcast='integer')
            df2 = df2.rename(columns={c:"Second doses given (n)"})
    for c in df.columns:
        if "(n)" in c:
            # the number of second doses due is the number of first doses given 14 w ago
            df = df.rename(columns={c:f"Second Doses due at {latest_date_fmt.replace(' 2021','')} (n)"})
            
    df = df2.join(df)
    
    df = df.rename(columns={"Total eligible":"Total population"})

    # only show tables where a significant proportion of the total population are due second dose
    df["Second Doses due (% of total)"] = 100*df[f"Second Doses due at {latest_date_fmt.replace(' 2021','')} (n)"]\
                                          /df["Total population"]
    if backend != "expectations" and (
        df["Second Doses due (% of total)"][("overall","overall")] < 0.70):
        continue    
    df = df.drop("Second Doses due (% of total)", 1)
    
    # calculate difference from expected
    df["Second doses given (% of due)"] = 100*(df[f"Second doses given (n)"]/\
                                                 df[f"Second Doses due at {latest_date_fmt.replace(' 2021','')} (n)"]).round(3)
                                             

        
    # column order
    df = df[[f"Second Doses due at {latest_date_fmt.replace(' 2021','')} (n)", 
             "Second doses given (n)", "Second doses given (% of due)", "Total population"]]

    export_path = os.path.join("..", "output", "second_doses")
    if not os.path.exists(export_path):
        os.makedirs(export_path)
    df.to_csv(os.path.join(export_path, f"{title}{suffix}.csv"), index=True)
    
    show_table(df, title, latest_date_fmt, show_carehomes=True)    
    
    df["Second doses overdue (% of due)"] = 100 - df["Second doses given (% of due)"]
    
    ######### plot charts
    
    if " LD " in title:
        title = title.replace("LD (aged 16-64) population", "people with learning disabilities (aged 16-64)")
    display(Markdown(f"## \n ## {title.replace('Cumulative ','').replace(' vaccination figures', 's overdue').title()}"))
    
    cats_to_include = ["Age band", "Ethnicity (broad categories)", 
                   "Index of Multiple Deprivation (quintiles)", "Dementia", 
                   "Learning disability", "Psychosis, schizophrenia, or bipolar"]
    cats = [c for c in df.index.levels[0] if c in cats_to_include]
    
    # find ymax
    ymax = df[["Second doses overdue (% of due)"]].loc[cats].max()[0]
    
    # find errors based on rounding
    # both num and denom are rounded to nearest 7 so both may be out by <=3 
    df["pos_error"] = 100*3/(df[f"Second Doses due at {latest_date_fmt.replace(' 2021','')} (n)"]-3)
    df["neg_error"] = 100*3/(df[f"Second Doses due at {latest_date_fmt.replace(' 2021','')} (n)"]+3)
    
    rows_of_charts = int(len(cats)/2 + (len(cats)%2)/2)
    fig, axs = plt.subplots(rows_of_charts, 2, figsize=(12, 4*rows_of_charts))
    
    # unpack all the axes subplots
    axes = axs.ravel()
    # turn off axes until they are used
    for ax in axes:
        ax.set_axis_off()
        
    # plot charts and display titles
    for n, cat in enumerate(cats):
        chart_title = "Second doses overdue (% of those due)\n by "+ cat
        dfp=df.loc[cat]
        dfp[["Second doses overdue (% of due)"]].plot.bar(title=chart_title, ax=axes[n], legend=False)
        # add errorbars
        axes[n].errorbar(dfp.index, dfp["Second doses overdue (% of due)"], # same location as each bar
                         yerr=[dfp["neg_error"], dfp["pos_error"]], #"First row contains the lower errors, the second row contains the upper errors."
                         fmt="none", # no markers or connecting lines
                         ecolor='k')
        axes[n].set_axis_on()
        axes[n].set_ylim([0, min(125, ymax*1.05)])
        axes[n].set_ylabel("Second doses overdue (%)")
        axes[n].set_xlabel(cat.title())
        
        # reduce tick label sizes
        if (cat == "Ethnicity (broad categories)") | (cat == "Index of Multiple Deprivation (quintiles)"):
            plt.setp(axes[n].get_xticklabels(), fontsize=8)
    plt.subplots_adjust(hspace=1)
    display(Markdown("Second doses which have not been given 14 weeks since the first dose"),
           Markdown("Error bars indicate possible error caused by rounding"))
        
    plt.show()
    

# -


