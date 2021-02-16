import os
import pandas as pd
from IPython.display import display, Markdown
from IPython.core.display import SVG
from collections import OrderedDict
from operator import itemgetter


# we create a dict for renaming population variables into suitable longer/correctly capitalised forms for presentation as titles
variable_renaming = {'ageband': "Age band",
                      'ageband_5yr': "Age band",
                      'sex': "Sex",
                      'bmi':"BMI",   
                      'ethnicity 6 groups':"Ethnicity (broad categories)",
                      'imd categories':"Index of Multiple Deprivation (quintiles)",
                      'chronic cardiac disease': 'Chronic cardiac disease',
                      'current copd': 'Current COPD',
                      'dialysis': 'Dialysis',
                      'dmards': 'DMARDs',
                      'dementia': 'Dementia',
                      'psychosis schiz bipolar': 'Psychosis, schizophrenia, or bipolar',
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
    for filetype in ["tables", "figures", "text"]:
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
                            pre_string="by ", tail_string=".svg",
                            files_to_exclude=["Cumulative vaccination figures.svg"]):
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
    pre_string: string found in filename AHEAD OF desired factor for sorting (e.g. for filename containing "by ageband" use "by ").
                filename will be split at this point.
    tail_string: string found in filename AFTER desired factor for sorting (e.g. for filename containing "by ageband.csv" use ".csv").
                filename will be truncated from this point. 
    files_to_exclude (list): any files in target folder not to be included
    
    '''
    savepath = get_savepath(subfolder=org_breakdown)
    
    if subfolder:  
        file_list = os.listdir(os.path.join(savepath[foldername], subfolder))
    else:
        file_list = os.listdir(savepath[foldername])
    
    for f in files_to_exclude:
        if f in file_list:
            file_list.remove(f)
    
    # restrict to population subset of interest based on string supplied
    file_list = [f for f in file_list if population_subset in f]

    # restrict to demographics subset of interest based on strings supplied
    if demographics_subset:   
        file_list = [f for f in file_list if any(d in f for d in demographics_subset)]
    
    if by_demographics_or_population=="demographics":
        sort_order = {'ethnicity 6 groups': 3,
             'imd categories': 4,
             'bmi': 5,
             'cancer excl lung and haem': 10,
             'chemo or radio': 11,
             'chronic cardiac disease': 6,
             'current copd': 7,
             'dementia': 14,
             'dialysis': 12,
             'dmards': 13,
             'haematological cancer': 9,
             'intel dis incl downs syndrome': 15,
             'lung cancer': 8,
             'psychosis schiz bipolar': 16,
             'sex': 2,
             'ssri': 17,
             'overall':0,
             'ageband':1}
    elif by_demographics_or_population=="population":
        sort_order = {'80+': 0,
         '70-79': 1,
         'care home': 2,
         'shielding': 3,
         'under 70s, not in other eligible groups shown': 4}
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



def show_chart(filepath, *, org_breakdown="", subfolder="", title="on"):
    '''
    Show chart from specified filepath. Rename filepaths for use as chart titles.
    
    Inputs:
    filepath (str):  file path
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
    
    if title == "on":
        title_string = filepath
        for v in variable_renaming: # replace short strings with full variable names
            title_string = title_string.replace(v, f"{variable_renaming[v]}")
        title_string = title_string.replace(" by","\n ### by").replace(".svg","")
        display(Markdown(f"### {title_string}"))
        if (len(subfolder)>0) & (~any(s in filepath for s in ["overall","sex","imd_categories"])):
            display(Markdown(f"Zero percentages may represent suppressed low numbers; raw numbers were rounded to nearest 7"))
           
    
    display(SVG(filename=imgpath))
    
    

def show_table(filename, latest_date_fmt, *, org_breakdown=None, show_carehomes=False, 
               rows_to_exclude = [],
               export_csv=True, suffix=""):
    '''
    Show table with specified filename. Rename row and column headers.
    
    Inputs:
    filename (str): name of file
    latest_date_fmt (str): latest date of vaccination in dataset
    org_breakdown (str)
    show_carehomes (bool): whether or not to show care homes table
    rows_to_exclude (list): list of variables to exlude from all tables
    export_csv (bool): whether or not to save table as csv
    
    Outputs:
    tab (dataframe): formatted table (preceded by title derived from filename & intro text)   
    '''
    savepath = get_savepath(org_breakdown)
    
    # get table
    tab = pd.read_csv(os.path.join(savepath["tables"], filename))
    
    # rename columns
    tab = tab.rename(columns={"category":"Category",
                              "group":"Group",
                              "stp_name":"STP Name",
                              "region":"Region",
                              "vaccinated":f"Vaccinated at {latest_date_fmt.replace(' 2021','')} (n)",
                              "percent":f"Vaccinated at {latest_date_fmt.replace(' 2021','')} (%)",
                              "total": "Total eligible",
                              "vaccinated 7d previous (percent)":"Previous week's vaccination coverage (%)",
                              "vaccinated 7d previous":"Previous week's vaccination figure (n)",
                              "Uptake over last 7d (percent)": "Vaccinated over last 7d (%)",
                              "Uptake over last 7d": "Vaccinated over last 7d (n)",
                              "Increase in uptake (%)": "Increase in coverage over last 7d (%)",
                              "proportion of 80+ population included (%)": "Proportion of 80+ population included (%)",
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
    
    # display title
    display(Markdown(f"## \n ## {title} \n Please refer to footnotes below table for information."))
    
    # export csvs
    if export_csv==True:
        export_path = os.path.join("..", "machine_readable_outputs", "table_csvs")
        if not os.path.exists(export_path):
            os.makedirs(export_path)
        tab.to_csv(os.path.join(export_path, f"{title}{suffix}.csv"), index=True)

    # display table
    display(tab)
    
    # display footnotes
    display(Markdown("**Footnotes:**\n"\
                       f"- Patient counts rounded to the nearest 7"))
    if (show_carehomes == True) & (title == "Cumulative vaccination figures among care home population"):
        display(Markdown(f"- Population includes those known to live in an elderly care home, based upon clinical coding."))
    else:
        display(Markdown(f"- Population excludes those known to live in an elderly care home, based upon clinical coding."))
    if org_breakdown=="stp":
        display(Markdown("- The percentage coverage of each STP population by TPP practices for over 80s is displayed, and STPs with less than 10% coverage are not shown.\n"\
                         "- The subset of the population covered by TPP in each STP may not be representative of the whole STP. \n"\
                         "- Practice-STP mappings and total 80+ population used to calculate the coverage are as of March 2020 and some borders and population sizes may have changed. \n"\
                         "- “Disparity in vaccination” figures may be subject to large variation caused by rounding of small numbers - an indication of the possible range of values is therefore shown; the specific groups compared are those with most disparity on a national level but may not represent the biggest disparity present within each STP. "
                          "- 'Date projected to reach 90%' is an estimate based on the previous 7 days' uptake; being 'unknown' indicates projection of >6mo (likely insufficient information)"))
    
    if variable_renaming["ssri"] in tab.index:
        display(Markdown("- SSRIs group excludes individuals with Psychosis/ schizophrenia/bipolar, Intellectual disability incl Down syndrome, or Dementia."))