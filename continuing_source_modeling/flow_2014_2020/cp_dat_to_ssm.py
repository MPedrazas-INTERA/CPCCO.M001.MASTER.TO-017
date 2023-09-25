'''
MIT License
Author:         Jacob B Fullerton
Date:           November 14, 2017
Company:        Intera Inc.
Usage:          Intended for internal use at Intera Inc. to populate 1D stomp files with the post-processed MODFLOW flow
                modeling results.
Instructions:   The script must be placed in a directory with three folders as described below:
                Containing Folder:
                    --> Folder 1)   Predictive flow model results   ** Optional
                    --> Folder 2)   "ssm"       ** Must exist with the name shown inside of the quotes
                    --> Folder 3)   "stomp"     ** Must exist with the name shown inside of the quotes
                The *.dat files will be copied to the appropriate ssm subfolders. The only key necessary for this to
                work is to ensure that the site names are consistent between the "stomp" and "ssm" sub-folders. This does
                not mean that the names must be exactly the same, but the site names must be preserved in their entirety
                with each respective subfolder between the "stomp" and "ssm" directories. An example of this would be as
                follows:
                    -->stomp
                        -->c14
                            -->116-KW-1
                                --> gw_conc_16-24.dat   ## File to be copied
                    -->ssm
                        -->c14
                            -->116-KW-1                 ## Location for file to be copied into
                            -->116-KW-1_mig1            ## Location for file to be copied into
                            -->116-KW-1_mig2            ## Location for file to be copied into
                            ...
                In the above example, this script will still copy the *.dat file to the appropriate folders in the ssm
                directory. Provided that the site name can be found in the various folders/scenarios of the same site,
                the script will copy the file into each sub-folder as depicted above. Constituent naming must also be
                identical for this script to work.

WARNING:        DO NOT USE SITE NAMES THAT HAVE IDENTICAL COMPLETE NAMES (e.g. '116-K-2_west' and '116-K-2_west_1'.
                BECAUSE OF THE NATURE OF DICTIONARIES THIS TYPE OF NAMING CONVENTION MAY OCCASIONALLY HAVE UNEXPECTED
                CONSEQUENCES WITH THE WAY I HAVE WRITTEN THE CODE. PLEASE VERIFY RESULTS IF THIS NAMING CONVENTION IS
                NECESSARY. MODIFICATION TO THIS SCRIPT MAY BE NECESSARY.

                ALSO, IF MORE THAN ONE *.DAT FILE IS PRESENT, ONLY ONE WILL BE SELECTED FOR COPYING, PLEASE BE AWARE
                OF THIS. IF MORE FILES NEED TO BE COPIED, THEN THIS SCRIPT CAN BE EASILY MODIFIED TO ACCOMPLISH THIS
                (SEE LINES 72-75).
'''
import os
from shutil import copyfile
# Props to @user13993 and @Nisan.H on stackoverflow.com for this elegant answer. Will recognize containing directory
# of this script and assign it to the 'folder' variable.
folder = os.path.dirname(os.path.realpath(__file__))
###     User Input Start    ###

###     User Input End    ###

# Create a list of the COCs included in the STOMP folder
cocs = next(os.walk(os.path.join(folder,'stomp')))[1]
# Create a dictionary of the waste sites to be evaluated per COC
stomp_list = {}
for coc in cocs:
    stomp_list[coc] = next(os.walk(os.path.join(folder,'stomp',coc)))[1]

del cocs

# Create a list of COCs included in the SSM folder
cocs = next(os.walk(os.path.join(folder,'ssm')))[1]
# Create a dictionary of the waste sites to be evaluated per COC
ssm_list = {}
for coc in cocs:
    ssm_list[coc] = next(os.walk(os.path.join(folder,'ssm',coc)))[1]

# Loop through all of the locations in the ssm folder and copy the appropriate *.dat file from the stomp directory
for coc in ssm_list:
    for ssm_site in ssm_list[coc]:
        for stomp_site in stomp_list[coc]:
            if stomp_site.lower() in ssm_site.lower():
                file = [x for x in next(os.walk(os.path.join(folder,'stomp',coc,stomp_site)))[2] if '1-24.dat' in x.lower()]
                src = os.path.join(folder,'stomp',coc,stomp_site,file[0])
                dst = os.path.join(folder,'ssm',coc,ssm_site,file[0])
                copyfile(src, dst)