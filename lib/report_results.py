import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

from datetime import datetime
import json
from IPython.display import display, Markdown


def create_output_dirs():
    """
    Creates the output directories that the graphs and CSVs are saved into.

    Returns:
        savepath: A dictionary where the key is a file type and the value is the path
            that should be used to save or retrieve files of that type.
    """
    # create /assign directories for exporting figures and tables
    savepath = {}
    for filetype in ["tables", "figures", "text"]:
        savepath[filetype] = os.path.abspath(os.path.join("..", "interim-outputs", filetype))
        os.makedirs(savepath[filetype], exist_ok=True)

    # create /assign directories for exporting csvs behind the figures & for tables
    savepath_figure_csvs = os.path.abspath(os.path.join("..", "machine_readable_outputs", "figure_csvs"))
    os.makedirs(savepath_figure_csvs, exist_ok=True)
    savepath_table_csvs = os.path.abspath(os.path.join("..", "machine_readable_outputs", "table_csvs"))
    os.makedirs(savepath_table_csvs, exist_ok=True)

    return savepath, savepath_figure_csvs, savepath_table_csvs


def find_and_save_latest_date(df, savepath, reference_column_name="covid_vacc_date"):
    """
    Finds the latest date of a vaccine given and formats as a string.
    """
    # query the data frame and pull out the latest date
    latest_date = df[df[reference_column_name] != 0][reference_column_name].max()

    # change that date into a better and more readable format for graphs
    latest_date_fmt = datetime.strptime(latest_date, "%Y-%m-%d").strftime("%d %b %Y")

    with open(os.path.join(savepath["text"], "latest_date.txt"), "w") as text_file:
        text_file.write(latest_date_fmt)

    return latest_date, latest_date_fmt

def cumulative_sums(df, groups_of_interest, latest_date):
    '''
    Calculate cumulative sums
    
    Args:
        df (dataframe): input data
        groups_of_interest (dict): subgroups to breakdown by (and column on which to filter for these groups)
    
    Returns:
        df_dict_out (dict): This dict is a mapping from a group name (e.g '80+') to another dict, which is a mapping from a                                 feature name (e.g. 'sex') to a dataframe containing cumulative sums of vaccination data per day. 
    
    '''

    # Creates an empty dict to collect results as passes through function 
    df_dict_out = {}

    # for each group within the desired groups, it filters to that particular group. it 
    # also selects columns of interest. For example, in care home, we are interested in 
    # sex, ageband and broad ethnicity groups. In the analysis of age bands we are interested
    # in much more detail such as comorbidies and ethnicity in 16 groups. 
    for group_title, group_label in groups_of_interest.items():
    
        # filter dataframe to eligible group
        if group_label == "other": # for "all others" filter out the defined groups above
            out = df.copy().loc[(~df["community_ageband"].isin(["care home","70-79","80+"]))]
            cols = ["sex","ageband", "ethnicity_6_groups", "ethnicity_16_groups","imd_categories",
                    "bmi","chronic_cardiac_disease", "current_copd", "dialysis", "dmards","ssri"]
        elif group_label=="care home": 
            out = df.copy().loc[(df[group_label]==group_title)]
            cols = ["sex", "ageband", "ethnicity_6_groups"]
        else:    # age groups
            out = df.copy().loc[(df[group_label]==group_title)]
            cols = ["sex","ethnicity_6_groups","ethnicity_16_groups", "imd_categories", 
                    "bmi", "chronic_cardiac_disease", "current_copd", "dialysis", "dmards", "dementia",
                    "psychosis_schiz_bipolar","intel_dis_incl_downs_syndrome","ssri",
                     "chemo_or_radio", "lung_cancer", "cancer_excl_lung_and_haem", "haematological_cancer"]


        # This creates an empty dictionary that is used as a temporary collection place for the processed figures    
        df_dict_temp = {}
        
        # overall figures
        total = out[["patient_id"]].nunique()[0]

        # Copies the dataframe but filters only to those who have had a vaccine recorded 
        out2 = out.copy().loc[(out["covid_vacc_flag"]=="vaccinated")]

        # group by date of covid vaccines to calculate cumulative sum of vaccines at each date of the campaign
        out2 = pd.DataFrame(out2.groupby(["covid_vacc_date"])[["patient_id"]].nunique().unstack().fillna(0).cumsum()).reset_index()
        out2 = out2.rename(columns={0:"overall"}).drop(["level_0"],1)

        # in case no vaccinations on latest date for some STPs/groups, insert the latest data as a new row with the required date:
        if out2["covid_vacc_date"].max()<latest_date:
            out2.loc[max(out2.index)+1] = [latest_date, out2["overall"].max()]

        # suppress low numbers
        out2["overall"] = out2["overall"].replace([1,2,3,4,5,6], 0).fillna(0).astype(int)
        
        # Makes the overall_total values into integers so can be used in equation
        out2["overall_total"] = total.astype(int)
        
        # create a percentage by dividing results by total
        out2["overall_percent"] = 100*(out2["overall"]/out2["overall_total"])
        df_dict_temp["overall"] = out2.set_index("covid_vacc_date")
        
        # figures by demographic/clinical features
        for feature in cols:
            
            if feature=="sex":
                out = out.loc[out[feature].isin(["M","F"])]

            # find total number of patients in each subgroup (e.g. no of males and no of females)
            totals = out.groupby([feature])[["patient_id"]].nunique().rename(columns={"patient_id":"total"}).transpose()
            
            # find total number of patients vaccinated in each subgroup (e.g. no of males and no of females),
                # cumulative at each date of the campaign
            out2 = out.copy().loc[(out["covid_vacc_flag"]=="vaccinated")]
            out2 = out2.groupby([feature, "covid_vacc_date"])["patient_id"].nunique().unstack(0)
            out2 = out2.fillna(0).cumsum()
            
            # suppress low numbers
            out2 = out2.replace([1,2,3,4,5,6], 0).fillna(0)
            # round other values to nearest 7
            out2 = 7*round(out2/7, 0)

            for c2 in out2.columns:
                out2[f"{c2}_total"] = totals[c2][0].astype(int)
                #calculate percentage
                out2[f"{c2}_percent"] = 100*(out2[c2]/out2[f"{c2}_total"])           
            
            # in case no vaccinations on latest date for some STPs/groups, insert the latest data as a new row with the required date:
            if out2.index.max()<latest_date:
                out2.loc[latest_date] = out2.max()
                
            df_dict_temp[feature] = out2
        
        df_dict_out[group_title] = df_dict_temp

    return df_dict_out


def make_vaccine_graphs(df, latest_date, savepath):

    # cumulative chart by day of total vaccines given
    dfp = df.copy().loc[(df["covid_vacc_date"]!=0)]
    dfp["group"] = np.where(dfp["community_ageband"].isin(["80+","70-79","care home"]), dfp["community_ageband"], "other")
    dfp = dfp.groupby(["covid_vacc_date","group"])[["patient_id"]].count()  
    dfp = dfp.unstack().fillna(0).cumsum().reset_index().replace([0,1,2,3,4,5],0) 

    dfp["covid_vacc_date"] = pd.to_datetime(dfp["covid_vacc_date"]).dt.strftime("%d %b")
    dfp = dfp.set_index("covid_vacc_date")
    dfp.columns = dfp.columns.droplevel()
    dfp["total"] = dfp.sum(axis=1)

    dfp.plot(legend=True, ds='steps-post')

    plt.xlabel("date", fontweight='bold')
    plt.xticks(rotation=90)
    plt.ylabel("number of patients vaccinated", fontweight='bold')
    plt.title(f"Cumulative vaccination figures to {latest_date}", fontsize=16)
    plt.savefig(os.path.join(savepath["figures"], f"Cumulative vaccination figures.svg"), dpi=300, bbox_inches='tight')
    plt.show()

def report_results(df_dict_cum, group, latest_date, breakdown=None):
    '''
    Summarise data at latest date, overall and by demographic/clinical features, and including change 
    from previous week.
    Processes one group (e.g. 80+) at a time so must be run within a loop to cover all required groups. 
    
    Args:
        df_dict_cum (dict): dictionary of cumulative sums 
        group (str): e.g. "80+" (one of first level index of df_dict_cum)
        breakdown (list): 
    
    Returns:
        out3 (Dataframe): summary data
    '''
    
    # creates 2 empty dataframes to collect results in 
    out = pd.DataFrame()
    out3 = pd.DataFrame()
    
    # If no breakdown into subgroups is specified, then breakdown are the keys of the group only
    if (breakdown == None) | (breakdown==[]):
        breakdown = df_dict_cum[group].keys()
    
    # for each category in the breakdown 
    for category in breakdown:
        out = df_dict_cum[group][category]

        # calculate changes: select only latest date and 7 days ago:
        latest = pd.to_datetime(out.index).max()
        lastweek = (latest + pd.DateOffset(days=-7)).strftime("%Y-%m-%d")
        lastweek = str(max(lastweek, out.index.min()))

        # filter to required values:
        # for groups with a population denominator, keep the percentage value only
        if group != "under 70s, not in other eligible groups shown":
            out = out.filter(regex='percent').round(1)
            col_str = " (percent)"
        # for groups with no denominator, keep the actual values only
        else:
            # totals and percent not needed
            out = out.filter(regex='^(?!.*total).*$')
            out = out.filter(regex='^(?!.*percent).*$')
            col_str = ""
        
        # if last week's exact date not present, fill in using latest values prior to required date
        if sum(out.index == lastweek)==0:
            out.loc[lastweek] = out.loc[out.index < lastweek].max()
            
        out = out.loc[[latest_date,lastweek],:].transpose()

        '''# if there is only one non-zero value, round the remaining values to avoid suppressed values being calculated
            for i in out2.index:
                if (out2.loc[i] == 0).astype(int).sum() == 1:  
                    out2.loc[i]=10*(out2.loc[i]/10).round(0)
            display(out2)'''
        
        out["weeklyrate"] = ((out[latest_date] - out[lastweek]).fillna(0)).round(1)
        out["Increase in uptake (%)"] = (100*(out["weeklyrate"]/out[lastweek]).fillna(0)).round(1)
        out["weeks_to_target"] = (90 - out[latest_date])/out["weeklyrate"]

        date_reached=pd.Series(dtype="datetime64[ns]", name="date_reached")

        for i in out.index:
            weeks_to_target = out["weeks_to_target"][i]
            if weeks_to_target <=0: #already reached target
                date_reached[i] = "reached"
            if weeks_to_target <25: # if 6mo+ until expected to reach target, assume too little data to tell
                date_reached[i] = (latest + pd.DateOffset(days=weeks_to_target*7)).strftime('%d-%b')
            else:
                date_reached[i] = "unknown"
        out = out.transpose().append(date_reached).transpose().drop("weeks_to_target",1)
        out = out[[lastweek,"weeklyrate","date_reached","Increase in uptake (%)"]].rename(columns={lastweek: f"vaccinated at {lastweek}{col_str}", "weeklyrate":f"Uptake over last 7d{col_str}", "date_reached":"Date projected to reach 90%"})    
        out.index = out.index.str.replace("_percent","")    
        out = out.reset_index().rename(columns={category:"group", "index":"group"})
        out["category"] = category
        out = out.set_index(["category","group"])


        ##### n, percent and total pop figures for latest date
        out2 = df_dict_cum[group][category].reset_index()
        out2 = out2.loc[out2["covid_vacc_date"]==latest_date].reset_index().set_index("covid_vacc_date").drop(["index"], 1).transpose()
        # split field names e.g. "M_percent" ->"M""percent"
        out2.index = pd.MultiIndex.from_tuples(out2.index.str.split('_').tolist())

        out2 = out2.unstack().reset_index(col_level=1)
        out2.columns = out2.columns.droplevel()
        out2 = out2.rename(columns={"index":"group", np.nan:"vaccinated"})
        out2["percent"] = out2["percent"].round(1)
        out2["category"] = category
        out2 = out2.set_index(["category","group"])

        out2 = out2.join(out)

        out3 = out3.append(out2)   

    if group == "under 70s, not in other eligible groups shown":
        out3 = out3.drop(["percent","total","Date projected to reach 90%"],1)
    else:
        out3 = out3.drop(["Increase in uptake (%)"],1)
    
    return out3


def summarise_data_by_group(result_dict, latest_date, groups=["80+", "70-79", "care home", "under 70s, not in other eligible groups shown"]):
    """
    This takes in the large result_dict that is created by cumulative_sums()
    and loops through the specified groups and applies the function 
    report results. It adds these results to a dictionary which it returns. 

    Args:
        results_dict (dict): dictionary that is created by running cumulative_sums()
        latest_date (datetime object): dt object that is created by running 
            find_and_save_latest_date()
        groups (list): groups of interest. Default is ["80+", "70-79", "care 
            home", "under 70s, not in other eligible groups shown"]

    Returns:
        dict (df_dict_latest): dictionary of the results of applying function 
            report_results()
    """

    # creates an empty dictionary to fill in 
    df_dict_latest = {}


    # loops through the specified groups and applis report results.
    for group in groups:
        out = report_results(result_dict, group, latest_date=latest_date)

        # results are added to the dict with the group name as key
        df_dict_latest[group] = out

    # return results
    return df_dict_latest




def round7(num):
    '''
    Round n to nearest 7 and output as integer
    
    Args:
        num(int/float): number to be rounded

    Returns:
        int: rounded to the nearest 7

    '''

    return ( int(7*round((num/7),0)) )


def create_summary_stats(df, summarised_data_dict,  formatted_latest_date, savepath, groups=["80+", "70-79", "care home", "under 70s, not in other eligible groups shown"]):
    """
    This takes in the large summarised_data_dict that is created by summarise_data_by_group()
    and the original dataframe and loops through the specified groups and rounds the values 
    of the number vaccinated to the nearest 7 using the function round7(). It then 
    adds the results to a new dictionary and returns this. 

    It also outputs the results into a text file. 

    Args:
        df (Dataframe): pandas dataframe that is created by the load_data() function
        summarised_data_dict (dict): dictionary that is created by running summarise_data_by_group()
        formatted_latest_date (str): str that is created by running 
            find_and_save_latest_date()
        groups (list): groups of interest. Default is ["80+", "70-79", "care 
            home", "under 70s, not in other eligible groups shown"]

    Returns:
        dict (summary_stats): dictionary of the results
    """

    # create a dict to store results for display and for exporting to a txt file
    summary_stats= {}

    # add in a key that is the formatted str of the latest date
    summary_stats[f"### As at {formatted_latest_date}"] = ""

    # get the total vaccinated and round to the nearest 7
    vaccinated_total = round7( df.loc[df["covid_vacc_date"]!=0]["patient_id"].nunique() )

    # add the results fo the summary_stats dict 
    summary_stats["**Total** population vaccinated in TPP"] = f"{vaccinated_total:,d}"

    # loop through the specified groups and calculate number vaccinated in the groups
    # add the results to the dict
    for group in groups:
        out = summarised_data_dict[group]
        vaccinated = round7(out.loc[("overall","overall")]["vaccinated"])
        if group != "under 70s, not in other eligible groups shown":
            percent = out.loc[("overall","overall")]["percent"].round(1)
            total = out.loc[("overall","overall")]["total"].astype(int)
            summary_stats[f"**{group}** population vaccinated"] = f"{vaccinated:,} ({percent}% of {total:,})"
            #out_str = f"**{k}** population vaccinated {vaccinated:,} ({percent}% of {total:,})"
        else:
            #out_str = f"**{k}** population vaccinated {vaccinated:,}"
            summary_stats[f"**{group}** population vaccinated"] = f"{vaccinated:,}"

    # count oxford vax as a proportion of total; filter to date of first vax only in case of patients having mixed types    
    oxford_vaccines = round7(df.copy().loc[df["covid_vacc_date"]==df["covid_vacc_oxford_date"]]["covid_vacc_flag_ox"].sum())
    ox_percent = round(100*oxford_vaccines/vaccinated_total, 1)
    second_doses = round7(df["covid_vacc_2nd"].sum())
    sd_percent = round(100*second_doses/vaccinated_total, 1)

    summary_stats[f"#### Vaccine types and second doses"] = ""
    summary_stats["Second doses (% of all vaccinated)"] = f"{second_doses:,} ({sd_percent}%)"
    summary_stats["Oxford-AZ vaccines (% of all first doses)"] = f"{oxford_vaccines:,} ({ox_percent}%)"

    # export summary stats to text file
    json.dump(summary_stats, open(os.path.join(savepath["text"], "summary_stats.txt"),'w'))

    return summary_stats


def create_detailed_summary_uptake(summarised_data_dict,  formatted_latest_date, savepath, groups=["80+", "70-79", "care home", "under 70s, not in other eligible groups shown"]):
    """
    This takes in the large summarised_data_dict that is created by summarise_data_by_group()
    and loops through the specified groups and displays this information to the user. 

    It also outputs the results into a machine readable csv file. 

    Args:
        summarised_data_dict (dict): dictionary that is created by running summarise_data_by_group()
        formatted_latest_date (str): str that is created by running 
            find_and_save_latest_date()
        groups (list): groups of interest. Default is ["80+", "70-79", "care 
            home", "under 70s, not in other eligible groups shown"]

    """
    pd.set_option('display.max_rows',200)

    # loops through the groups and displays markdown
    for group in groups:
        display(Markdown(f"## "),
                Markdown(f"## COVID vaccination rollout among **{group}** population up to {formatted_latest_date}"),
                Markdown(f"- 'Date projected to reach 90%' being 'unknown' indicates projection of >6mo (likely insufficient information)\n"\
                           f"- Patient counts rounded to the nearest 7"))
        out = summarised_data_dict[group]
        # suppress previous week's values if change in vaccinated number is <10
        '''    if group!="under 70s, not in other eligible groups shown":
            out["Uptake over last 7d (percent)"]=np.where(out["Uptake over last 7d (percent)"]*out["total"]>=1000, 
                                                          out["Uptake over last 7d (percent)"],0)
            out["vaccinated at 2020-12-30 (percent)"]=np.where(out["Uptake over last 7d (percent)"]*out["total"]>=1000, 
                                                                out["vaccinated at 2020-12-30 (percent)"],0)'''
        display(out)

        # saves to file
        out_csv = out.copy()
        if "Date projected to reach 90%" in out.columns:
            out_csv = out_csv.drop("Date projected to reach 90%",1)
        out_csv.to_csv(os.path.join(savepath["tables"], f"Cumulative vaccination figures among {group} population.csv"), index=True)


def plot_dem_charts(summary_stats_results, cumulative_data_dict, formatted_latest_date, savepath, savepath_figure_csvs, include_overall=False):

    # get the overall rate of >80 years olds and strip out the text to get the number (should be within 0 - 100)
    overall_rate_80 = float(summary_stats_results["**80+** population vaccinated"].split(" ")[1][1:5])

    if include_overall==False:
        groups = ["sex","ethnicity_6_groups","imd_categories", "bmi", "chronic_cardiac_disease", "current_copd", "dialysis", "dmards",
                    "psychosis_schiz_bipolar","intel_dis_incl_downs_syndrome","dementia", "ssri",
                     "chemo_or_radio", "lung_cancer", "cancer_excl_lung_and_haem", "haematological_cancer"]
    else:
        groups = ["overall","sex","ethnicity_6_groups","imd_categories", "bmi", "chronic_cardiac_disease", "current_copd", "dialysis", "dmards",
                    "psychosis_schiz_bipolar","intel_dis_incl_downs_syndrome","dementia", "ssri",
                     "chemo_or_radio", "lung_cancer", "cancer_excl_lung_and_haem", "haematological_cancer"]
   
   
    for k in ["80+"]:
        display(Markdown(f"## COVID vaccination rollout among **{k}** population up to {formatted_latest_date}"))

        out=cumulative_data_dict[k]
        for c in groups:
            out=cumulative_data_dict[k][c]
            # suppress low numbers         
            cols = out.columns[(~out.columns.str.contains("_percent")) & (~out.columns.str.contains("_total"))]
            for c2 in cols:
                #  drop vaccinated and total column but keep percentage
                out = out.drop([c2, f"{c2}_total"],1)
                out = out.rename(columns={f"{c2}_percent":c2})

            display(Markdown(f"### COVID vaccinations among **{k}** population by **{c.replace('_',' ')}**"))
            out = out.reset_index()
            out["covid_vacc_date"] = pd.to_datetime(out["covid_vacc_date"]).dt.strftime("%d %b")
            out = out.set_index("covid_vacc_date")
            out.to_csv(os.path.join(savepath_figure_csvs, f"Cumulative vaccination percent among {k} population by {c.replace('_',' ')}.csv"), index=True)

            out.plot(legend=True, ds='steps-post')
            plt.axhline(overall_rate_80, color="k", linestyle="--", alpha=0.5)
            plt.text(0, overall_rate_80*1.02, "latest overall national* rate")
            plt.ylim(top=1.1*max(overall_rate_80, out.max().max()))
            plt.ylabel("Percent vaccinated (cumulative)")
            plt.xlabel("Date vaccinated")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            plt.savefig(os.path.join(savepath["figures"], f"COVID vaccinations among {k} population by {c.replace('_',' ')}.svg"), dpi=300, bbox_inches='tight')

            plt.show() 