'This produces summary tables and charts for second or third doses due/overdue.'


import matplotlib.pyplot as plt

from IPython.display import display, Markdown
import os
import pandas as pd
import sys
sys.path.append('../lib/')
from create_report import import_table, show_table

def abbreviate_time_period(time_period):
    '''
    This takes in a string that describes a length of time unit
    (e.g., '4 weeks', '91 days') and converts it to a short form.

    INPUTS
    time_period (str): a period of time

    OUTPUTS
    time_period_abbr (str): the first letter of the unit
    '''
    time_period_abbr = time_period.replace(" ", "").replace('days', "d").replace(
        'weeks', "w").replace('months', "m").replace('years', "y")
    return( time_period_abbr )


def second_third_doses(tablelist, tablelist_2nd, cohorts=None, *, org_breakdown=None, dose_type="Second", time_period="14 weeks", latest_date_fmt, latest_date_fmt_2,
                       max_ylim=12, 
                       backend="expectations", suffix = "_tpp"):
    
    '''
    This produces summary tables and charts for second or third doses due/overdue.
    
    
    INPUTS
    tablelist (list): list of tables, each containing data for a single cohort on the "previous" dose (1st or 2nd)
    tablelist_2nd (list):  list of tables, each containing data for a single cohort on the dose of interest (2nd or 3rd)
    org_breakdown (str): Type of org breakdown (e.g "stp"); also used for patient subsets (e.g., "u16")
    dose_type (str): "Second" or "Third"
    time_period (str): E.g. "14 weeks"
    latest_date_fmt (str): latest date of any vaccines
    latest_date_fmt (str): e.g. "3rd July 2020" - formatted version of cut-off date up to which vaccines due were calculated
    cohorts (list): cohorts to include e.g. ["80+", "70-79"]
    max_ylim (int): max value for ymax (puts a limit on ymax to prevent chart axes being set by one rogue value). 
    backend (str): backend
    suffix (str): backend string to append to filenames
    
    OUTPUTS
    A summary table and chart for each cohort, broken down into various subgroups
    Also a summary table with one line per cohort.
    '''
    
    # set up other variables needed:
    if dose_type=="Second":
         previous_dose = "first" 
    elif dose_type=="Third":
         previous_dose = "second" 
    else:
        assert False, f"unexpected dose_type: {dose_type}"
    
    dose_file_name = f"{dose_type.lower()}_doses"
    
    # create empty df for summary results ("overall" row for each cohort)
    summary = pd.DataFrame()

    ### Can't embed this in the f string below due to curly brackets
    date_string = latest_date_fmt.replace(' 202\d{1}','')

    for f, f2 in zip(tablelist, tablelist_2nd):
        df, _ = import_table(f, latest_date_fmt=latest_date_fmt_2, org_breakdown=org_breakdown, show_carehomes=True, suffix=suffix, export_csv=False)
        df = df.drop(columns=["Previous week's vaccination coverage (%)", "Total eligible", "Vaccinated over last 7d (%)"])

        df2, title = import_table(f2, latest_date_fmt, org_breakdown=org_breakdown, show_carehomes=True, suffix=suffix, export_csv=False)
        df2 = df2.drop(columns=["Previous week's vaccination coverage (%)", "Vaccinated over last 7d (%)"])

        # column renaming and number formatting
        for c in df2.columns:
            if "(n)" in c:
                df2[c] = pd.to_numeric(df2[c], downcast='integer')
                df2 = df2.rename(columns={c:f"{dose_type} doses given (n)"})
        for c in df.columns:
            if "(n)" in c:
                # the number of doses due is the number of previous doses given <time period> ago
                df = df.rename(columns={c:f"{dose_type} Doses due at {date_string} (n)"})

        df = df2.join(df)

        df = df.rename(columns={"Total eligible":"Total population"})

        # only show tables where a significant proportion of the total population are due second dose
        df[f"{dose_type} Doses due (% of total)"] = 100*df[f"{dose_type} Doses due at {date_string} (n)"]\
                                              /df["Total population"]
        if backend != "expectations" and (
            df[f"{dose_type} Doses due (% of total)"][("overall","overall")] < 0.50):
            continue    
        df = df.drop(columns=f"{dose_type} Doses due (% of total)")

        # calculate difference from expected
        df[f"{dose_type} doses given (% of due)"] = 100*(df[f"{dose_type} doses given (n)"]/\
                                                     df[f"{dose_type} Doses due at {date_string} (n)"]).round(3)

        df[f"{dose_type} doses overdue (n)"] = df[f"{dose_type} Doses due at {date_string} (n)"] -\
                                          df[f"{dose_type} doses given (n)"]

        # column order
        df = df[[f"{dose_type} Doses due at {date_string} (n)", f"{dose_type} doses overdue (n)",
                 f"{dose_type} doses given (n)", f"{dose_type} doses given (% of due)", "Total population"]]

        export_path = os.path.join("..", "output", "machine_readable_outputs", dose_file_name)
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        df.to_csv(os.path.join(export_path, f"{title}{suffix}.csv"), index=True)


        ######### create summary by extracting "overall" row
        pop_overall = df.loc[("overall","overall")]
        pop_overall = pop_overall.rename(title.replace(f"Cumulative {dose_type.lower()} dose vaccination figures among ","").replace(" population",""))
        summary = summary.append(pop_overall)
        
        # if a list of cohorts have been supplied, exit loop here for groups not in cohorts
        if cohorts:
            if any(c in title for c in cohorts)==False: 
                continue
                
        display(Markdown("[Back to top](#Contents)"))
        
        # add comma separators to numbers before displaying table
        df_to_show = df.copy()
        column_list = [
            f"{dose_type} Doses due at {date_string} (n)", 
            f"{dose_type} doses overdue (n)", f"{dose_type} doses given (n)", "Total population"
            ]

        show_table(df_to_show, title, latest_date_fmt, count_columns=column_list, show_carehomes=True)    

        df[f"{dose_type} doses overdue (% of due)"] = 100 - df[f"{dose_type} doses given (% of due)"]


        ######### plot charts

        if " LD " in title:
            title = title.replace("LD (aged 16-64) population", "people with learning disabilities (aged 16-64)")
        display(Markdown(f"## \n ## {title.replace('Cumulative ','').replace(' vaccination figures', 's overdue').title()}"))

        cats_to_include = ["Age band", "Ethnicity (broad categories)", 
                       "Index of Multiple Deprivation (quintiles)", "Dementia", 
                       "Learning disability", "Psychosis, schizophrenia, or bipolar", "Housebound", 
                        "brand of first dose"]
        cats = [c for c in df.index.levels[0] if c in cats_to_include]
        df = df.loc[cats]

        # find errors based on rounding
        # both num and denom are rounded to nearest 7 so both may be out by <=3 
        df["pos_error"] = 100*3/(df[f"{dose_type} Doses due at {date_string} (n)"]-3)
        df["neg_error"] = 100*3/(df[f"{dose_type} Doses due at {date_string} (n)"]+3)

        # do not show in charts values representing less than 100 people
        df.loc[df[f"{dose_type} Doses due at {date_string} (n)"] < 100,
                 [f"{dose_type} doses overdue (% of due)","neg_error","pos_error"]] = 0

        # find ymax
        ymax = df[[f"{dose_type} doses overdue (% of due)"]].max()[0]

        rows_of_charts = int(len(cats)/2 + (len(cats)%2)/2)
        fig, axs = plt.subplots(rows_of_charts, 2, figsize=(12, 4*rows_of_charts))

        # unpack all the axes subplots
        axes = axs.ravel()
        # turn off axes until they are used
        for ax in axes:
            ax.set_axis_off()

        # plot charts and display titles
        for n, cat in enumerate(cats):
            chart_title = f"{dose_type} doses overdue (% of those due)\n by "+ cat
            dfp=df.copy().loc[cat]

            # do not include "unknown" brand of first dose (unless it's the only item in the index)
            if (cat == f"brand of {previous_dose} dose") & (len(dfp.index)>1):
                dfp = dfp.loc[dfp.index!="Unknown"]



            # plot chart
            dfp[[f"{dose_type} doses overdue (% of due)"]].plot.bar(title=chart_title, ax=axes[n], legend=False)
            # add errorbars
            axes[n].errorbar(dfp.index, dfp[f"{dose_type} doses overdue (% of due)"], # same location as each bar
                             yerr=[dfp["neg_error"], dfp["pos_error"]], #"First row contains the lower errors, the second row contains the upper errors."
                             fmt="none", # no markers or connecting lines
                             ecolor='k')
            axes[n].set_axis_on()

            axes[n].set_ylim([0, min(max_ylim, ymax*1.05)])
            axes[n].set_ylabel(f"{dose_type} doses overdue (%)")
            axes[n].set_xlabel(cat.title())

            # reduce tick label sizes
            if cat in ("Ethnicity (broad categories)", "Index of Multiple Deprivation (quintiles)"):
                plt.setp(axes[n].get_xticklabels(), fontsize=8)
        plt.subplots_adjust(hspace=1)

        display(Markdown(f"{dose_type} doses which have not been given at least {time_period} since the {previous_dose} dose"),
               Markdown("Error bars indicate possible error caused by rounding"))

        plt.show()

    # show summary table (first improve number formatting)
    for c in summary:
        if "(n)" in c or "Total population" in c:
                summary[c] = summary[c].astype(int).apply('{:,}'.format)
    display(Markdown(f"## \n # Summary"), summary)
