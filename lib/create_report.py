import os
import pandas as pd
from IPython.display import display, Markdown
from collections import OrderedDict
from operator import itemgetter
from os.path import exists


# we create a dict for renaming population variables into suitable longer/correctly capitalised forms for presentation as titles
variable_renaming = { 'ageband 5yr': "Age band",
                      'ageband': "Age band",
                      'sex': "Sex",
                      'bmi':"BMI",   
                      'housebound':'Housebound',
                      'ethnicity 6 groups':"Ethnicity (broad categories)",
                      'imd categories':"Index of Multiple Deprivation (quintiles)",
                      'chronic cardiac disease': 'Chronic cardiac disease',
                      'current copd': 'Current COPD',
                      'ckd': 'Chronic kidney disease',
                      'dmards': 'DMARDs',
                      'dementia': 'Dementia',
                      'psychosis schiz bipolar': 'Psychosis, schizophrenia, or bipolar',
                      'LD': 'Learning disability',
                      'intel dis incl downs syndrome': 'Intellectual disability inc Down syndrome',
                      'ssri': 'SSRI (last 12 months)',
                      'chemo or radio': 'Chemo or radiotherapy',
                      'lung cancer': 'Cancer (lung)',
                      'cancer excl lung and haem': 'Cancer (excluding lung/haem)',
                      'haematological cancer': 'Cancer (haematological)'}


def get_savepath(subfolder=None):
    '''
    Create /assign directories for importing figures and tables
    
    Inputs:
    subfolder (str): subfolder of in which to find files
    
    output:
    savepath (dict): a dictionary of filepaths for each file type
    '''
    
    savepath = {}
    for filetype in ["tables", "figures", "text", "objects"]:
        if subfolder:
            savepath[filetype] = os.path.abspath(os.path.join("..", "interim-outputs", subfolder, filetype))   
        else:
            savepath[filetype] = os.path.abspath(os.path.join("..", "interim-outputs", filetype))
            
    return(savepath)
    
    
def find_and_sort_filenames(foldername, *, 
                            org_breakdown=None,
                            subfolder="",
                            by_demographics_or_population="demographics", 
                            population_subset="80+",
                            demographics_subset=[],
                            file_extension="csv",
                            pre_string="by ", tail_string=None,
                            files_to_exclude=None):
    '''
    List files from specified folder ("figures" or "tables") and sort in predetermined order
    
    Inputs:
    foldername (str):   Name of target folder in which "figures" or "tables" are found
    org_breakdown (str): Type of org breakdown (e.g "stp")
    subfolder (str): subfolder of in which to find files (e.g an individual org)
    by_demographics_or_population (str): type of sort
    population_subset (str): population group to include
    demographics_subset (list): list of strings to filter filenames to a subset of demographic features
                                (e.g. ["ethnicity_6_groups", "imd_categories"])
    file_extension (str): extension of the files to list (use to pick out either SVGs or PNGs)
    pre_string: string found in filename AHEAD OF desired factor for sorting (e.g. for filename containing "by ageband" use "by ").
                filename will be split at this point.
    tail_string: string found in filename AFTER desired factor for sorting (e.g. for filename containing "by ageband.csv" use ".csv").
                filename will be truncated from this point. 
    files_to_exclude (list): any files in target folder not to be included
    
    '''
    tail_string = tail_string or f".{file_extension}"
    files_to_exclude = files_to_exclude or [f"Cumulative vaccination figures.{file_extension}"]

    savepath = get_savepath(subfolder=org_breakdown)
    
    if subfolder:  
        file_list = os.listdir(os.path.join(savepath[foldername], subfolder))
    else:
        file_list = os.listdir(savepath[foldername])
    
    for f in files_to_exclude:
        if f in file_list:
            file_list.remove(f)

    # restrict to files with the specified extension
    file_list = [f for f in file_list if f.endswith(f".{file_extension}")]

    # restrict to population subset of interest based on string supplied
    file_list = [f for f in file_list if population_subset in f]

    # restrict to demographics subset of interest based on strings supplied
    if demographics_subset:   
        file_list = [f for f in file_list if any(d in f for d in demographics_subset)]
    
    if by_demographics_or_population=="demographics":
        ordered_dems = ['overall',
                        'newly shielded since feb 15',
                        'ageband',
                        'ageband_5yr',
                        'sex',
                        'ethnicity 6 groups',
                        'imd categories',
                        'bmi',
                        'housebound',
                        'chronic cardiac disease',
                        'current copd',
                        'lung cancer',
                        'haematological cancer',
                        'cancer excl lung and haem',
                        'chemo or radio',
                        'ckd',
                        'dmards',
                        'dementia',
                        'LD',
                        'psychosis schiz bipolar',
                        'ssri'
                        ]
        sort_order = {key: ix for ix, key in enumerate(ordered_dems)}
    elif by_demographics_or_population=="population":
        ordered_pops = ['80+', '70-79', 'care home', 'shielding (aged 16-69)', '65-69', 'LD (aged 16-64)', '60-64', '55-59', '50-54','40-49', '30-39', '18-29', '16-49, not in other eligible groups shown']
        sort_order = {key: ix for ix, key in enumerate(ordered_pops)}
    else:
        display("sort_by_population_or_demographics received an invalid value")
        
    sort_order2 = {}
    for item in file_list:
        group = item.split(pre_string)[1].replace(tail_string, "") 
        if group in sort_order:
            sort_order2[item] = sort_order[group]
        # handle new items not in pre-sorted list by adding them to end
        elif len(sort_order2)==0: 
            # if no items yet in new dict simply use max value from pre-sorted list and add 1
            sort_order2[item] = 1 + max(sort_order.values())
        else: # if some items already in new dict, one or more new items may already have been added     
            sort_order2[item] = 1 + max(max(sort_order.values()), 
                                    max(sort_order2.values())) 
        

    out_list = OrderedDict(sorted(sort_order2.items(), key=itemgetter(1)))
    return(out_list.keys())


def show_chart(filepath, image_format, org_breakdown="", subfolder="", title="on"):
    '''
    Show chart from specified filepath. Rename filepaths for use as chart titles.
    
    Inputs:
    filepath (str):  file path
    image_format (ImageFormat): the type of image to show
    org_breakdown (str): Type of org breakdown (e.g "stp")
    subfolder (str): subfolder of in which to find files (e.g. an individual STP)
    title (str): "on" or "off"
    
    Outputs:
    plot     
    '''
    savepath = get_savepath(org_breakdown)
    
    if subfolder:     
        imgpath = os.path.join(savepath["figures"], subfolder, filepath)
    else:
        imgpath = os.path.join(savepath["figures"], filepath)
    
    if exists(imgpath): 
        if title == "on":
            title_string = filepath

            for v in variable_renaming: # replace short strings with full variable names
                title_string = title_string.replace(v, f"{variable_renaming[v]}")
            title_string = title_string.replace(" by","\n ### by").replace(f".{image_format.extension}", "")
            display(Markdown(f"### {title_string}"))
            if (len(subfolder)>0) & (~any(s in filepath for s in ["overall","sex","imd_categories"])):
                display(Markdown(f"Zero percentages may represent suppressed low numbers; raw numbers were rounded to nearest 7"))
            
        display(image_format.formatter(filename=imgpath))


def import_table(filename, latest_date_fmt, *, org_breakdown=None, show_carehomes=False, 
               rows_to_exclude = [],
               export_csv=True, suffix=""):
    '''
    Show table with specified filename. Rename row and column headers.
    
    Inputs:
    filename (str): name of file
    latest_date_fmt (str): latest date of vaccination in dataset
    org_breakdown (str): Type of org breakdown (e.g "stp"); also used for patient subsets (e.g., "u16")
    show_carehomes (bool): whether or not to show care homes table
    rows_to_exclude (list): list of variables to exlude from all tables
    export_csv (bool): whether or not to save table as csv
    
    Outputs:
    tab (dataframe): formatted table 
    title (str): title to display with table
    '''
    savepath = get_savepath(org_breakdown)

    # get table
    tab = pd.read_csv(os.path.join(savepath["tables"], filename))
    
    ### Can't embed this in the f string below due to curly brackets
    date_string = latest_date_fmt.replace(' 202\d{1}','')
    
    # rename columns
    tab = tab.rename(columns={"category":"Category",
                              "group":"Group",
                              "stp_name":"STP Name",
                              "region":"Region",
                              "vaccinated":f"Vaccinated at {date_string} (n)",
                              "percent":f"Vaccinated at {date_string} (%)",
                              "total": "Total eligible",
                              "vaccinated 7d previous (percent)":"Previous week's vaccination coverage (%)",
                              "vaccinated 7d previous":"Previous week's vaccination figure (n)",
                              "Uptake over last 7d (percent)": "Vaccinated over last 7d (%)",
                              "Uptake over last 7d": "Vaccinated over last 7d (n)",
                              "Increase in uptake (%)": "Increase in coverage over last 7d (%)",
                              "proportion of 80+ population included (%)": "Proportion of 80+ population included (%)",
                              "STP rate, to date (percent)": "STP rate, to date (% of due)",
                              "STP rate, last 7d (percent)": "STP rate, last 7d (% of due)",
                              "[White - Black] abs difference": "White-Black ethncity: disparity in vaccination % (abs difference +/- range of uncertainty)", 
                              "[5 Least deprived - 1 Most deprived] abs difference": "Least deprived - Most deprived IMD quintile: disparity in vaccination % (abs difference +/- range of uncertainty)"})
    
    # for "national" reports, exclude any specified rows and set index
    if "Category" in tab.columns:
        if rows_to_exclude:
            for i in rows_to_exclude:
                tab = tab.loc[tab["Category"]!=i]
        tab["Category"] = tab["Category"].str.replace("_"," ")
        tab = tab.set_index(["Category", "Group"])
    
    # for stp reports, set STP as index
    if org_breakdown=="stp":
        tab = tab.set_index(["STP Name"]).sort_index()
        
    # rename variables as per reference table above
    tab = tab.rename(variable_renaming,
                      axis='index')
    
    # get title from filename
    title = filename.replace(".csv","")
    
    # do not return care home table if specified
    if (show_carehomes==False) & (title == "Cumulative vaccination figures among care home population"):
        return
    
    # export csvs
    if export_csv==True:
        export_path = os.path.join("..", "output", "machine_readable_outputs", "table_csvs")
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        tab.to_csv(os.path.join(export_path, f"{title}{suffix}.csv"), index=True)

    # return table and title
    return tab, title
    

        
def show_table(df, title, latest_date_fmt, *, count_columns=[], org_breakdown=None, show_carehomes=False, perc_only=False, stp_summary=False, stp_pop_coverage=False):
    '''
    Show table with specified filename. Rename row and column headers.
    
    Inputs:
    df: dataframe
    latest_date_fmt (str): latest date of vaccination in dataset
    count_columns (list): a list of columns (str) to format with commas
    org_breakdown (str): e.g. "stp"
    show_carehomes (bool): whether or not we are showing care homes table
    perc_only (bool): to indicate whether only percentages are being presented; if so, the footnote regarding rounding to 7 need not be displayed
    stp_summary (bool): to indicate whether summarised STP data are being presented; if so, footnotes specific to non-summarised data will not be displayed
    stp_pop_coverage (bool): to indicate whether STP population coverage data are being presented; if so, 
    
    Outputs:
    tab (dataframe): formatted table (preceded by title derived from filename & intro text)   
    '''
    
    # get table
    tab = df
       
    # display title
    if " LD " in title:
        title = title.replace("LD", "Learning Disabilities")
    display(Markdown(f"## \n ## {title} \n Please refer to footnotes below table for information."))
    
    if org_breakdown == "stp":
        if stp_pop_coverage:
            display(Markdown("The percentage coverage of each STP population by TPP practices is shown below. \
                The 'Adequate coverage' column indicates whether at least 10% of the STP population is available in TPP \
                (the 10% threshold is an arbitrary cutoff)."))
        else:
            display(Markdown("Vaccination coverage is calculated as a percentage of those who are due their booster/third dose. \
                              Note that STPs with less than 10% population coverage in TPP practices are not shown."))

    tab_to_show = tab.copy()
    for c in count_columns:
        tab_to_show[c] = tab_to_show[c].apply('{:,}'.format)

    # display table
    display(tab_to_show)
    
    display(Markdown("**Footnotes:**\n"))

    # display footnotes
    if ( not perc_only ):
        display(Markdown(f"- Patient counts rounded to the nearest 7."))
    
    if ("second" in title.lower()):
        display(Markdown(f"- Only persons who are currently registered and had their first dose at least 14 weeks ago are included in the 'due' group."))
        
    # display caveats about care home inclusion/exclusion where relevant
    if (show_carehomes == True) & ("care home" in title):
        display(Markdown(f"- Population includes those known to live in an elderly care home, based upon clinical coding."))
    elif "shielding" in title:
        display(Markdown(f"- Population excludes those over 65 known to live in an elderly care home, based upon clinical coding."))
    elif ("80+" in title) | ("70-79" in title) | ("65-69" in title): # don't include under 65s here
        display(Markdown(f"- Population excludes those known to live in an elderly care home, based upon clinical coding."))
    
    # display note that 65-69 and LD group excludes shielding subgroup
    if ("65-69" in title) | ("60-64" in title)  | ("55-59" in title) | ("50-54" in title) | ("Learning Disabilities" in title):
        display(Markdown(f"- Population excludes those who are shielding."))
    
    # display footnotes related to STPs   
    if org_breakdown=="stp":
        display(Markdown("- The subset of the population covered by TPP in each STP may not be representative of the whole STP."))
        display(Markdown("- Practice-STP mappings used to calculate the coverage are as of March 2020 and some borders and population sizes may have changed."))

        if not stp_summary:
            display(Markdown("- “Disparity in vaccination” figures may be subject to large variation caused by rounding of small numbers - an indication of the possible range of values is therefore shown; the specific groups compared are those with most disparity on a national level but may not represent the biggest disparity present within each STP."))
            display(Markdown("- 'Date projected to reach 90%' is an estimate based on the previous 7 days' uptake; being 'unknown' indicates projection of >6mo (likely insufficient information)."))

    if variable_renaming["ssri"] in tab.index:
        display(Markdown("- SSRIs group excludes individuals with Psychosis/ schizophrenia/bipolar, LD, or Dementia."))
    
    if variable_renaming["ckd"] in tab.index:
        display(Markdown(f"- Chronic kidney disease is defined as the presence of a relevant diagnostic code, or a most recent stage recorded >= 3."))
    

        
        
def df_column_switch(df, column1, column2):
    i = list(df.columns)
    a, b = i.index(column1), i.index(column2)
    i[b], i[a] = i[a], i[b]
    df = df[i]
    return df
