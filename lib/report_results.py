import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

from datetime import datetime
from IPython.display import display, Markdown


def create_output_dirs(subfolder=None):
    """
    Creates the output directories that the graphs and CSVs are saved into.
    
    Args:
        subfolder (str): option to create folders within a subfolder of the name supplied

    Returns:
        savepath: A dictionary where the key is a file type and the value is the path
            that should be used to save or retrieve files of that type.
        savepath_figure_csvs, savepath_table_csvs: String file paths
    """
    # create /assign directories for exporting figures and tables
    savepath = {}
    for filetype in ["tables", "figures", "text"]:
        if subfolder:
            savepath[filetype] = os.path.abspath(os.path.join("..", "interim-outputs", subfolder, filetype))
        else:
            savepath[filetype] = os.path.abspath(os.path.join("..", "interim-outputs", filetype))
        os.makedirs(savepath[filetype], exist_ok=True)

    # create /assign directories for exporting csvs behind the figures & for tables
    savepath_figure_csvs = os.path.abspath(os.path.join("..", "machine_readable_outputs", "figure_csvs"))
    os.makedirs(savepath_figure_csvs, exist_ok=True)
    savepath_table_csvs = os.path.abspath(os.path.join("..", "machine_readable_outputs", "table_csvs"))
    os.makedirs(savepath_table_csvs, exist_ok=True)

    return savepath, savepath_figure_csvs, savepath_table_csvs


def create_output_dirs_per_org(org_list=None, subfolder=None, filetypes=["figures"]):
    """
    Creates output directories for each org that the graphs and CSVs are saved into.
    
    Args:
        org_list (list): list of strings (organisations)
        subfolder (str): create folders within a subfolder of the name supplied
        filetypes (list)

    Returns:
        savepath_org_list: A dictionary where the key is a file type and the value is the path
            that should be used to save or retrieve files of that type.
    """
    # create /assign directories for exporting figures and tables
    savepath, _, _ = create_output_dirs(subfolder=subfolder)
    savepath_orgs = {}
    
    for filetype in filetypes:
        savepath_orgs[filetype] = {}
        for org in org_list:
            savepath_orgs[filetype][org] = os.path.abspath(os.path.join(savepath[filetype], org))
            os.makedirs(savepath_orgs[filetype][org], exist_ok=True)

    return savepath_orgs


def find_and_save_latest_date(df, savepath, reference_column_name="covid_vacc_date"):
    """
    Finds the latest date of a date column and formats as a string.
    
    Inputs:
    df (dataframe): must contain `reference_column_name`
    savepath (str): location to save latest date as a txt file
    reference_column_name (str): column of dates in which to find latest date
    
    Returns:
    latest_date (str): "%Y-%m-%d"
    latest_date_fmt (str): "%d %b %Y"
    """
    # query the data frame and pull out the latest date
    latest_date = df[df[reference_column_name] != 0][reference_column_name].max()

    # change that date into a better and more readable format for graphs
    latest_date_fmt = datetime.strptime(latest_date, "%Y-%m-%d").strftime("%d %b %Y")

    with open(os.path.join(savepath["text"], "latest_date.txt"), "w") as text_file:
        text_file.write(latest_date_fmt)

    return latest_date, latest_date_fmt


def filtering(d):
    '''
    Find items from the full set of single digit numbers (0-9) which are not present as values in a given dict
    
    Inputs:
    d (dict): a dict mapping strings to numeric `values`
    
    Outputs:
    l (list): a list containing zero and all the single digit numbers (0-9) which do not appear in d
    
    '''
    all_keys = [0,1,2,3,4,5,6,7,8,9]
    keys = list(d.values())

    # check which of `all_keys` are absent in `keys` and return them as a list (but always include 0)
    l = [k for k in all_keys if ((k not in keys)|(k==0))]
    return l


def cumulative_sums(df, groups_of_interest, features_dict, latest_date, reference_column_name="covid_vacc_date"):
    '''
    Calculate cumulative sums across groups
    
    Args:
        df (dataframe): input data
        groups_of_interest (dict): dict mapping names of population/eligible subgroups to integers (1-9, and 0 for "other")
        features_dict (dict): dictionary mapping population subgroups to a list of demographic/clinical factors to include for that group
        latest_date (str): "YYYY-MM-DD"
        reference_column_name (str): e.g. "covid_vacc_date" for first dose, "covid_vacc_second_dose_date" for second dose
    
    Returns:
        df_dict_out (dict): This dict is a mapping from a group name (e.g '80+') to another dict, which is a mapping from a feature name (e.g. 'sex') to a dataframe containing cumulative sums of vaccination data per day. 
    '''

    # Creates an empty dict to collect results as passes through function 
    df_dict_out = {}
    
    # for each group within the desired groups, it filters to that particular group. it 
    # also selects columns of interest. For example, in care home, we are interested in 
    # sex, ageband and broad ethnicity groups. In the analysis of age bands we are interested
    # in much more detail such as comorbidities and ethnicity in 16 groups. 
    
    # make a new field for the priority groups we are looking at (where any we have not specifically listed are regrouped as 0/"other")
    items_to_group = filtering(groups_of_interest)
    df["group"] = np.where(df["priority_group"].isin(items_to_group), 0, df["priority_group"])
    # translate number into name
    for name, number in groups_of_interest.items():
        df.loc[df["group"]==number, "group_name"] = name
    
    for group_title, group_label in groups_of_interest.items():
        out = df.copy().loc[(df["group"]==group_label)]
            
        # define columns to include, ie. a list of features of interest (e.g. ageband, ethnicity) per population group 
        if group_title in features_dict:
            cols = features_dict[group_title]
        elif group_label in features_dict: ## "other" group
            cols = features_dict[group_label]
        else: # for age bands use all available features
            cols =  features_dict["DEFAULT"]

        
        df_dict_temp = filtered_cumulative_sum(df=out, columns=cols, latest_date=latest_date, reference_column_name=reference_column_name)

        
        df_dict_out[group_title] = df_dict_temp

    return df_dict_out


def filtered_cumulative_sum(df, columns, latest_date, reference_column_name="covid_vacc_date"):
    """
    This calculates cumulative sums for a dataframe, and when given a set of
    characteristics as columns, produces a dictionary of dataframes.

    Args:
        df (Dataframe): pandas dataframe. At the very least this needs a column with a date in
            YYYY-MM-DD format, a column called 'covid_vacc_date' and a 'covid_vacc_flag'.
        columns (list): list of subgroups e.g. ageband, sex
        latest_date (datetime object): the date of the latest date of counting vaccines
        reference_column_name (str): e.g. "covid_vacc_date" for first dose, "covid_vacc_second_dose_date" for second dose

    Returns:
        Dict (of dataframes): Each dataframe produced has a date as a row, with the value of the number
            of vaccinations, the total that could be vaccinated (i.e. the denominator) and
            the cumulative percentage vaccinated.

            For overall population, i.e no subgroups, if the initial value is less that 7, it is
            rounded to 0. For subgroups, the numerator (i.e the number of people who had a vaccine)
            is rounded to the nearest 7.
    """
    # This creates an empty dictionary that is used as a temporary collection place for the processed figures    
    df_dict_temp = {}
    
    # overall figures
    total = df[["patient_id"]].nunique()[0]

    # Copies the dataframe but filters only to those who have had a vaccine recorded 
    filtered = df.copy().loc[(df[reference_column_name]!=0)]

    # group by date of covid vaccines to calculate cumulative sum of vaccines at each date of the campaign
    out2 = pd.DataFrame(filtered.groupby([reference_column_name])[["patient_id"]].nunique().unstack().fillna(0).cumsum()).reset_index()
    out2 = out2.rename(columns={0:"overall"}).drop(["level_0"],1)

    # filter to latest date and earlier (usually no effect unless a date earlier than the latest available data is passed)
    out2 = out2.loc[out2[reference_column_name] <= latest_date]
    
    # in case no vaccinations on latest date for some orgs/groups, insert the latest data as a new row with the required date:    
    if latest_date not in list(out2[reference_column_name]):
        out2.loc[max(out2.index)+1] = [latest_date, out2.loc[out2[reference_column_name]<latest_date]["overall"].max()]

    # suppress low numbers
    out2["overall"] = out2["overall"].replace([1,2,3,4,5,6], 0).fillna(0).astype(int)
    
    # Rounds the overall_total values (and makes into integers)
    out2["overall_total"] = round7(total)    
    
    # create a percentage by dividing results by total
    out2[f"overall_percent"] = 100*(out2["overall"]/out2["overall_total"])
  
    df_dict_temp["overall"] = out2.set_index(reference_column_name)
    
    # figures by demographic/clinical features
    for feature in columns:
        if feature=="sex":
            df = df.loc[df[feature].isin(["M","F"])]
            filtered = filtered.loc[filtered[feature].isin(["M","F"])]

        # find total number of patients in each subgroup (e.g. no of males and no of females)
        totals = df.groupby([feature])[["patient_id"]].nunique().rename(columns={"patient_id":"total"}).transpose()
        # suppress low numbers
        totals = totals.replace([1,2,3,4,5,6], 0).fillna(0)
        totals = round7(totals)
    
        # find total number of patients vaccinated in each subgroup (e.g. no of males and no of females),
            # cumulative at each date of the campaign
        out2 = filtered.copy().groupby([feature, reference_column_name])["patient_id"].nunique().unstack(0)
        out2 = out2.fillna(0).cumsum()

        # filter to latest date and earlier (usually no effect unless a date earlier than the latest available data is passed)
        out2 = out2.loc[out2.index <= latest_date]
        
        # suppress low numbers
        out2 = out2.replace([1,2,3,4,5,6], 0).fillna(0)
        # round other values to nearest 7
        out2 = round7(out2)

        for c2 in out2.columns:
            out2[f"{c2}_total"] = totals[c2][0].astype(int)
            #calculate percentage
            out2[f"{c2}_percent"] = 100*(out2[c2]/out2[f"{c2}_total"])   
            
        # in case no vaccinations on latest date for some orgs/groups, insert the latest data as a new row with the required date
        if out2.index.max()<latest_date:
            out2.loc[latest_date] = out2.max()
            
        df_dict_temp[feature] = out2

    return df_dict_temp


def make_vaccine_graphs(df, latest_date, savepath, savepath_figure_csvs, vaccine_type="first_dose", suffix=""):
    '''
    Cumulative chart by day of total vaccines given across key eligible groups. Produces both SVG and PNG versions.
    
    Args:
        df (dataframe): cumulative daily data on vaccines given per group
        latest_date (str): latest date across dataset in YYYY-MM-DD format
        savepath (dict): path to save figure (savepath["figures"])
        savepath_figure_csvs (str): path to save machine readable csv for recreating the chart
        vaccine_type (str): used in output strings to describe type of vaccine received e.g. "first_dose", "moderna". 
                            Also appended to filename of output. 
        suffix (str)
    '''
    
    if vaccine_type=="first_dose":
        reference_column_name="covid_vacc_date"
        title=f"Cumulative vaccination figures"
    else:
        reference_column_name=f"covid_vacc_{vaccine_type}_date"
        title=f"Cumulative {vaccine_type.replace('_',' ')} vaccination figures"   
    
    dfp = df.copy().loc[(df[reference_column_name]!=0)]

    dfp = dfp.groupby([reference_column_name,"group_name"])[["patient_id"]].count()  
    dfp = dfp.unstack().fillna(0).cumsum().reset_index().replace([0,1,2,3,4,5,6],0) 
    
    dfp[reference_column_name] = pd.to_datetime(dfp[reference_column_name]).dt.strftime("%d %b")
    dfp = dfp.set_index(reference_column_name)
    dfp = round7(dfp)
    
    dfp.columns = dfp.columns.droplevel()
    dfp["total"] = dfp.sum(axis=1)
    
    # sort columns (eligible groups) such that they appear in descending order of total no of vaccines at the latest date, 
    # legend entries will appear in corresponding order hence be easier to read
    dfp = dfp.sort_values(by=dfp.last_valid_index(), axis=1, ascending=False)
    
    
    # export data to csv
    out = dfp.copy()
    if savepath_figure_csvs:
        out.to_csv(os.path.join(savepath_figure_csvs, f"{title} among each eligible group{suffix}.csv"), index=True)
    
    # divide numbers into millions if exceeding 10m, otherwise thousands
    if dfp["total"].max() >= 1e7:
        dfp = dfp/1e6
        ylabel = "number of patients (millions)"
    else:
        dfp = dfp/1000
        ylabel = "number of patients (thousands)"
    
    # plot chart
    dfp.plot(legend=True, ds='steps-post')

    # set chart labels and other options
    plt.xlabel("date", fontweight='bold')
    plt.xticks(rotation=90)
    plt.ylabel(ylabel, fontweight='bold')
    plt.title(f"{title} to {latest_date}", fontsize=16)
    plt.legend(bbox_to_anchor=(1.04,1), loc="upper left")
    
    # export figure to file and display it
    filename = os.path.join(savepath["figures"], title)
    plt.savefig(f"{filename}.svg", dpi=300, bbox_inches='tight')
    plt.savefig(f"{filename}.png", dpi=300, bbox_inches='tight')
    plt.show()
    

    
def report_results(df_dict_cum, group, latest_date, breakdown=None):
    '''
    Summarise data at latest date, overall and by demographic/clinical features, and including change 
    from previous week.
    Processes one group (e.g. 80+) at a time so must be run within a loop to cover all required groups. 
    
    Args:
        df_dict_cum (dict): dictionary of cumulative sums 
        group (str): e.g. "80+" (one of first level index of df_dict_cum)
        latest_date (str): latest date across dataset in YYYY-MM-DD format
        breakdown (list): demographic/clinical features to display in breakdown
    
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
        reference_column_name = out.index.name

#         # filter to latest_date and earlier (allows a date other than the current date to be passed)
#         out = out.loc[out.index <= latest_date]
#         if latest_date not in list(out.index):
#             out.loc[latest_date] = out.loc[out.index <latest_date].max()

        # calculate changes: select only latest date and 7 days ago:
        latest = pd.to_datetime(out.index).max()
        lastweek = (latest + pd.DateOffset(days=-7)).strftime("%Y-%m-%d")
        lastweek = str(max(lastweek, out.index.min()))

        # filter to required values:
        # for groups with a population denominator, keep the percentage value only
        if "not in other eligible groups" not in group:
            out = out.filter(regex='percent').round(1)
            col_str = " (percent)"
        # for groups with no denominator, keep the actual values only
        else:
            # totals and percent not needed
            out = out.filter(regex='^(?!.*total).*$')
            out = out.filter(regex='^(?!.*percent).*$')
            col_str = ""
        
        

        # if last week's exact date not present, fill in using latest values prior to required date
        if lastweek not in list(out.index):
            out.loc[lastweek] = out.loc[out.index < lastweek].max()
        out = out.loc[[latest_date,lastweek],:].transpose()
        
        out["weeklyrate"] = ((out[latest_date] - out[lastweek]).fillna(0)).round(1)
        out["Increase in uptake (%)"] = (100*(out["weeklyrate"]/out[lastweek]).fillna(0)).round(1)
        out["weeks_to_target"] = (90 - out[latest_date])/out["weeklyrate"]

        date_reached=pd.Series(dtype="datetime64[ns]", name="date_reached")

        for i in out.index:
            weeks_to_target = out["weeks_to_target"][i]
            if (weeks_to_target <=0): #already reached target
                date_reached[i] = "reached"
            elif weeks_to_target <25: # if 6mo+ until expected to reach target, assume too little data to tell
                date_reached[i] = (latest + pd.DateOffset(days=weeks_to_target*7)).strftime('%d-%b')
            else:
                date_reached[i] = "unknown"
        out = out.transpose().append(date_reached).transpose().drop("weeks_to_target",1)
        out = out[[lastweek,"weeklyrate","date_reached","Increase in uptake (%)"]].rename(columns={lastweek: f"vaccinated 7d previous{col_str}", "weeklyrate":f"Uptake over last 7d{col_str}", "date_reached":"Date projected to reach 90%"})    
        out.index = out.index.str.replace("_percent","")    
        out = out.reset_index().rename(columns={category:"group", "index":"group"})
        out["category"] = category
        out = out.set_index(["category","group"])


        ##### n, percent and total pop figures for latest date
        out2 = df_dict_cum[group][category].reset_index()
        out2 = out2.loc[out2[reference_column_name]==latest_date].reset_index().set_index(reference_column_name).drop(["index"], 1).transpose()
        # split field names e.g. "M_percent" ->"M""percent"
        
        out2.index = pd.MultiIndex.from_tuples(out2.index.str.split('_').tolist())
        out2 = out2.unstack().reset_index(col_level=1)
        out2.columns = out2.columns.droplevel()
        out2 = out2.rename(columns={"index":"group", np.nan:"vaccinated"}).fillna(0)
        out2["percent"] = out2["percent"].round(1)
        out2["category"] = category
        out2 = out2.set_index(["category","group"])

        out2 = out2.join(out)

        out3 = out3.append(out2)   

    if "not in other eligible groups" in group:
        out3 = out3.drop(["percent","total","Date projected to reach 90%"],1)
    else:
        out3 = out3.drop(["Increase in uptake (%)"],1)
    
    return out3


def summarise_data_by_group(result_dict, latest_date, 
                            groups=["80+", "70-79", "care home", "shielding (aged 16-69)"]):
    """
    This takes in the large result_dict that is created by cumulative_sums()
    and loops through the specified groups and applies the function 
    report results. It adds these results to a dictionary which it returns. 

    Args:
        results_dict (dict): dictionary that is created by running cumulative_sums()
        latest_date (datetime object): dt object that is created by running 
            find_and_save_latest_date()
        groups (list): groups of interest. 

    Returns:
        dict (df_dict_latest): dictionary of the results of applying function 
            report_results()
    """

    # creates an empty dict to fill in 
    df_dict_latest = {}


    # loops through the specified groups and applies report_results.
    for group in groups:
        out = report_results(result_dict, group, latest_date=latest_date)

        # results are added to the dict with the group name as key
        df_dict_latest[group] = out

    # return results
    return df_dict_latest


def round7(input_):
    '''
    Round input_ to nearest 7 
    
    Args:
        input_ (int/float/df/series): number or dataframe to be rounded

    Returns:
        int/df/series: rounded to the nearest 7

    '''
    if (isinstance(input_, pd.DataFrame)) | (isinstance(input_, pd.Series)):
        return ( 7*round((input_/7),0) )
    else:
        return ( int(7*round((input_/7),0)) )


def create_summary_stats(df, summarised_data_dict,  formatted_latest_date, savepath,  vaccine_type="first_dose",
                         groups=["80+", "70-79", "care home", "shielding (aged 16-69)"],
                         suffix=""):
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
        savepath (dict): location to save summary stats
        vaccine_type (str): used in output strings to describe type of vaccine received e.g. "first_dose", "moderna". 
                            Also appended to filename of output. 
        groups (list): groups of interest. 
        suffix (str): provider name to append to output

    Returns:
        dict (summary_stats): dictionary of the results
    """

    # create a series to store results for display and exporting
    summary_stats= pd.Series(dtype="str", name=f"{vaccine_type.replace('_',' ')} as at {formatted_latest_date}")
    additional_stats =  pd.Series(dtype="str", name=f"Vaccine types and second doses")
    
    # get the total vaccinated and round to the nearest 7
    if vaccine_type=="first_dose":
        reference_column_name="covid_vacc_date"
    else:
        reference_column_name=f"covid_vacc_{vaccine_type}_date"
    vaccinated_total = round7( df.loc[df[reference_column_name]!=0]["patient_id"].nunique() )

    # add the results fo the summary_stats dict 
    suffix_str = suffix.replace("_","").upper()
    summary_stats[f"Total vaccinated in {suffix_str}"] = f"{vaccinated_total:,d}"

    # loop through the specified groups and calculate number vaccinated in the groups
    # add the results to the dict
    for group in groups:
        out = summarised_data_dict[group]
        vaccinated = round7(out.loc[("overall","overall")]["vaccinated"])
        if "not in other eligible groups" not in group:
            percent = out.loc[("overall","overall")]["percent"].round(1)
            total = out.loc[("overall","overall")]["total"].astype(int)
            summary_stats[f"{group}"] = f"{percent}% ({vaccinated:,} of {total:,})"
            #out_str = f"**{k}** population vaccinated {vaccinated:,} ({percent}% of {total:,})"
        else:
            #out_str = f"**{k}** population vaccinated {vaccinated:,}"
            summary_stats[f"{group}"] = f"{vaccinated:,}"

    # if summarising first doses, perform some additional calculations        
    if vaccine_type=="first_dose":        
        # count each vax type as a proportion of total; filter to date of first vax only in case of patients having mixed types    
        oxford_vaccines = round7(df.copy().loc[df["covid_vacc_date"]==df["covid_vacc_oxford_date"]]["covid_vacc_flag_ox"].sum())
        ox_percent = round(100*oxford_vaccines/vaccinated_total, 1)
        pfizer_vaccines = round7(df.copy().loc[df["covid_vacc_date"]==df["covid_vacc_pfizer_date"]]["covid_vacc_flag_pfz"].sum())
        pfz_percent = round(100*pfizer_vaccines/vaccinated_total, 1)
        moderna_vaccines = round7(df.copy().loc[df["covid_vacc_date"]==df["covid_vacc_moderna_date"]]["covid_vacc_flag_mod"].sum())
        mod_percent = round(100*moderna_vaccines/vaccinated_total, 1)
        
        # second doses
        second_doses = round7(df["covid_vacc_2nd"].sum())
        sd_percent = round(100*second_doses/vaccinated_total, 1)
        mixed_ox_pfz_doses = round7(df["covid_vacc_ox_pfz"].sum())
        mixed_ox_pfz_percent = round(100*mixed_ox_pfz_doses/second_doses, 1)
        mixed_ox_mod_doses = round7(df["covid_vacc_ox_mod"].sum())
        mixed_ox_mod_percent = round(100*mixed_ox_mod_doses/second_doses, 1)
        mixed_mod_pfz_doses = round7(df["covid_vacc_mod_pfz"].sum())
        mixed_mod_pfz_percent = round(100*mixed_mod_pfz_doses/second_doses, 1)

        additional_stats["Oxford-AZ vaccines (% of all first doses)"] = f"**{ox_percent}%** ({oxford_vaccines:,})"
        additional_stats["Pfizer vaccines (% of all first doses)"] = f"**{pfz_percent}%** ({pfizer_vaccines:,})"
        additional_stats["Moderna vaccines (% of all first doses)"] = f"**{mod_percent}%** ({moderna_vaccines:,})"
        
        additional_stats["Second doses (% of all vaccinated)"] = f"**{sd_percent}%** ({second_doses:,})"
        
        additional_stats["Mixed doses Ox-AZ + Pfizer (% of fully vaccinated)"] = f"**{mixed_ox_pfz_percent}%** ({mixed_ox_pfz_doses})"
        additional_stats["Mixed doses Ox-AZ + Moderna (% of fully vaccinated)"] = f"**{mixed_ox_mod_percent}%** ({mixed_ox_mod_doses})"
        additional_stats["Mixed doses Moderna + Pfizer (% of fully vaccinated)"] = f"**{mixed_mod_pfz_percent}%** ({mixed_mod_pfz_doses})"

    # export summary stats to text file
    summary_stats.to_csv(os.path.join(savepath["text"], f"summary_stats_{vaccine_type}.txt"))
    additional_stats.to_csv(os.path.join(savepath["text"], f"additional_stats_{vaccine_type}.txt"))

    return summary_stats, additional_stats


def create_detailed_summary_uptake(summarised_data_dict,  formatted_latest_date, savepath, vaccine_type="first_dose", groups=["80+", "70-79", "care home", "shielding (aged 16-69)"]):
    """
    This takes in the large summarised_data_dict that is created by summarise_data_by_group()
    and loops through the specified groups and displays this information to the user. 

    It also outputs the results into a machine readable csv file. 

    Args:
        summarised_data_dict (dict): dictionary that is created by running summarise_data_by_group()
        formatted_latest_date (str): str that is created by running 
            find_and_save_latest_date()
        savepath (str): save path.
        vaccine_type (str): string to insert into filename on export.
        groups (list): eligible groups of interest. 

    """
    pd.set_option('display.max_rows',200)
    # loops through the groups and displays markdown
    for group in groups:
        display(Markdown(f"## "),
                Markdown(f"## COVID vaccination rollout ({vaccine_type.replace('_', ' ')}) among **{group}** population up to {formatted_latest_date}"),
                Markdown(f"- 'Date projected to reach 90%' being 'unknown' indicates projection of >6mo (likely insufficient information)\n"\
                           f"- Patient counts rounded to the nearest 7"))
        out = summarised_data_dict[group]
        for c in ["vaccinated","total"]:
            if c in out.columns:
                out[c] = out[c].astype(int)
        display(out)

        # saves to file
        out_csv = out.copy()
        if "Date projected to reach 90%" in out.columns:
            out_csv = out_csv.drop("Date projected to reach 90%",1)
        
        if vaccine_type == "first_dose":
            out_str = ""
        else:
            out_str = vaccine_type.replace("_", " ") + " "
        out_csv.to_csv(os.path.join(savepath["tables"], f"Cumulative {out_str}vaccination figures among {group} population.csv"), index=True)

        

def plot_dem_charts(summary_stats_results, cumulative_data_dict, formatted_latest_date, savepath, pop_subgroups=["80+", "70-79"], groups_dict=None, groups_to_exclude=None, savepath_figure_csvs=None, include_overall=False, org_name="", suffix=""):
    
    '''
    Plot vaccine coverage charts by demographic features. Produces both SVG and PNG versions.
    
    Args:
        summary_stats_results (dict): summary statistics for full cohort to use for plotting comparator lines
        cumulative_data_dict (dict): dictionary of dataframes to plot
        formatted_latest_date (str): string describing latest datapoint found across entire dataseet
        savepath (dict): Dictionary mapping filetypes (in this case "figures") to filepaths. 
                         If org_name is supplied this dict should map filetypes to orgs to filepaths.
        pop_subgroups (list): population subgroups for which to create charts, default ["80+", "70-79"]
        groups_dict (dict): dictionary mapping population subgroups to a list of demographic/clinical factors to include for that group
        groups_to_exclude (list):
        savepath_figure_csvs (dict): Optionally supply if exporting numbers presented in charts to csv
        include_overall (bool): Option to include "overall" chart ie. chart with a single line, not broken down into any groups
        org_name (str): name of organisation for which data is to be presented (e.g. an STP or region)
        suffix (str): suffix to append to filenames on export
    '''
    
    # set up a default list of characteristics
    groups = ["sex","ethnicity_6_groups","imd_categories"]        

   
    if len(org_name)>1:
        org_string = f" for {org_name}"
    else:
        org_string = ""

    for k in pop_subgroups:
        
        if groups_dict: # if specific demographic/clinical groups have been provided for each population subgroup, overwrite them here
            if k in groups_dict:
                groups = groups_dict[k]
            else:
                groups = groups_dict["DEFAULT"]
        
        if groups_to_exclude:
            groups = [e for e in groups if e not in groups_to_exclude]
            
        if include_overall==True:
            groups.insert(0, "overall")
        
        # display title for section of charts
        display(Markdown(f"## \n ## COVID vaccination rollout among **{k}** population up to {formatted_latest_date}{org_string}"))

        # get the overall vaccination rate among relevant group and strip out the text to get the number (should be within 0 - 100)
        overall_rate = float(summary_stats_results[f"{k}"][0:4].replace("%",""))
    
        out=cumulative_data_dict[k]
        
        for c in groups:
            out=cumulative_data_dict[k][c]
                     
            # get index name (== "covid_vacc_date" for first doses)
            reference_column_name = out.index.name
            vaccine_type = reference_column_name.replace("covid_vacc_","").replace("date","").replace("_"," ").title()
            
            # export csv to file - numerator and denominator rather than percentages
            if savepath_figure_csvs:
                cols = [c for c in out.columns if '_percent' not in c]
                out_csv = out.copy()[cols]
                
                out_csv.to_csv(os.path.join(savepath_figure_csvs, f"Cumulative {vaccine_type}vaccination percent among {k} population by {c.replace('_',' ')}{suffix}.csv"), index=True)
            
            #  for plotting, drop vaccinated and total column but keep percentage
            cols = [c for c in out.columns if ('_percent' not in c) & ('_total' not in c)]
            for c2 in cols:
                out = out.drop([c2, f"{c2}_total"],1)
                out = out.rename(columns={f"{c2}_percent":c2})

            # display title and caveats for individual chart
            display(Markdown(f"### {vaccine_type}COVID vaccinations among **{k}** population by **{c.replace('_',' ')}**"))
            if len(org_name)>0:
                display(Markdown(f"#### {org_string}"))
                if ~(c in ["overall","sex","imd_categories"]):
                    display(Markdown(f"Zero percentages may represent suppressed low numbers; raw numbers were rounded to nearest 7"))
            
            
            out = out.reset_index()
            out[reference_column_name] = pd.to_datetime(out[reference_column_name]).dt.strftime("%d %b")
            out = out.set_index(reference_column_name)
            
            
            # plot trend chart and set chart options
            out.plot(legend=True, ds='steps-post')
            plt.axhline(overall_rate, color="k", linestyle="--", alpha=0.5)
            plt.text(0, overall_rate*1.02, "latest overall cohort rate")
            plt.ylim(top=1.1*max(overall_rate, out.max().max()))
            plt.ylabel("Percent (cumulative)")
            plt.xlabel("Date")
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            
            # export figures to file
            if len(org_name)>0:
                figure_savepath = savepath["figures"][org_name]          
            else: 
                figure_savepath = savepath["figures"]
            filename = os.path.join(figure_savepath, f"{vaccine_type}COVID vaccinations among {k} population by {c.replace('_', ' ')}")
            plt.savefig(f"{filename}.svg", dpi=300, bbox_inches='tight')
            plt.savefig(f"{filename}.png", dpi=300, bbox_inches='tight')

            plt.show() 