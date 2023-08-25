'''
MIT License
Author:         Jacob B Fullerton
Date:           November 10, 2017
Company:        Intera Inc.
Usage:          Intended for internal use at Intera Inc. to populate 1D stomp files with the post-processed MODFLOW flow
                modeling results.
Instructions:   The script must be placed in a directory with three folders as described below:
                Containing Folder:
                    --> Folder 1)   Predictive flow model results
                    --> Folder 2)   "ssm"   ** This is optional for this script as this script does not read this folder
                    --> Folder 3)   "stomp"     ** Must exist with the name shown inside of the quotes
                The contents of the predictive flow model results must be the *.csv post-processed results by waste site
                whose naming convention is:
                    "make_BC_[waste site name].csv"
                The [waste site name] is essential to keep consistent throughout each directory. In order to distinguish
                between the [waste site name] and the other parts of the naming convention for the predictive model
                results, the user will have to specify the first part and ensure that the [waste site name] immediately
                preceeds the ".csv" in the filename. I.E.:
                    "[naming prefix][waste site name].csv"
                The user only needs to specify the [naming prefix], the script will decipher the [waste site name].

                This script will only copy the predictive flow model results into the STOMP input files (those with the
                "[waste site name].tpl" file format).

WARNING:        DO NOT USE SITE NAMES THAT HAVE IDENTICAL COMPLETE NAMES (e.g. '116-K-2_west' and '116-K-2_west_1'.
                BECAUSE OF THE NATURE OF DICTIONARIES THIS TYPE OF NAMING CONVENTION MAY OCCASIONALLY HAVE UNEXPECTED
                CONSEQUENCES WITH THE WAY I HAVE WRITTEN THE CODE. PLEASE VERIFY RESULTS IF THIS NAMING CONVENTION IS
                NECESSARY. MODIFICATION TO THIS SCRIPT MAY BE NECESSARY.

Edited by R.Weatherl June 2022

'''
import os
# from sys import exit

## folder = os.path.dirname(os.path.realpath(__file__))  ## old syntax
folder = os.getcwd() ## for windows

###     User Input Start    ###

# [naming prefix]
prefix = 'make_BC_'

# Key for the west face of the column
up_gradient_key = '|up_gradient_cell|'

# Key for the east face of the column
down_gradient_key = '|down_gradient_cell|'

# STOMP input file name (for both template and actual input files)
name = 'input_cycle2'

###     User Input End    ###
# Obtain the folder containing the post-processed flow results
for directory in next(os.walk(folder))[1]:
    if 'ssm' in directory.lower():
        pass
    elif 'stomp' in directory.lower():
        pass
    elif 'plots' in directory.lower():
        pass
    else:
        pred_flow = directory.lower()

# Create a list of the COCs included in the STOMP folder
cocs = next(os.walk(os.path.join(folder,'stomp')))[1]
# Create a dictionary of the waste sites to be evaluated per COC
coc_list = {}
for coc in cocs:
    coc_list[coc] = next(os.walk(os.path.join(folder,'stomp',coc)))[1]

# Read in each *.csv file from the predictive flow model results into a dictionary with the [waste site name] as the key
flow_results = {}
for file in next(os.walk(os.path.join(folder, pred_flow)))[2]:
    if file.startswith("make_BC_"):
        with open(os.path.join(folder,pred_flow,file),'r') as rows:
            i = 0
            for row in rows:
                if i == 0:
                    i += 1
                    pass
                else:
                    text = row.split('"').pop(-2)
                    key = file.replace(prefix,'').replace('.csv','')
                    if key not in flow_results:
                        cell = row.split('"').pop(1)
                        flow_results[key] = {'down': [text], 'up': []}
                    else:
                        if cell != row.split('"').pop(1):
                            flow_results[key]['up'] += [text]
                        else:
                            flow_results[key]['down'] += [text]
for coc in coc_list:
    for site in coc_list[coc]:    ## if len(coc_list) > 1 --> [coc_list[coc]]. else --> coc_list[coc]
        print(site)
        with open(os.path.join(folder,'stomp',coc,site, name + '.tpl'),'r') as template:
            with open(os.path.join(folder,'stomp',coc,site,name),'w') as file:
                for t_line in template:
                    try:
                        if up_gradient_key not in t_line and down_gradient_key not in t_line:
                            file.write(t_line)
                        elif up_gradient_key in t_line:
                            try:
                                for f_line in flow_results[site]['up']:
                                    file.write(f_line)
                                    file.write('\n')
                            except:
                                for flow_site in flow_results:
                                    if flow_site in site:
                                        for f_line in flow_results[flow_site]['up']:
                                            file.write(f_line)
                                            file.write('\n')
                                        break
                                if flow_site not in site:
                                    print(
                                        'There is an error with the naming convention. Please verify the files and naming ' +
                                        'conventions.\n')
                                    print('The script failed with the coc/site name: ' + coc + '/' + site)
                                    exit()
                        else:
                            try:
                                for f_line in flow_results[site]['down']:
                                    file.write(f_line)
                                    file.write('\n')
                            except:
                                for flow_site in flow_results:
                                    if flow_site in site:
                                        for f_line in flow_results[flow_site]['down']:
                                            file.write(f_line)
                                            file.write('\n')
                                        break
                                if flow_site not in site:
                                    print(
                                        'There is an error with the naming convention. Please verify the files and naming ' +
                                        'conventions.\n')
                                    print('The script failed with the coc/site name: ' + coc + '/' + site)
                                    exit()
                    except:
                        exit()