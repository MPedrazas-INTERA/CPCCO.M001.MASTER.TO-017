
"""
Script to combine output images of simulated plumes
User defines:
- file path within function
- figure dimensions within function (depending on how many images per fig)
- figure output name
- list of scenarios of interest
- list of images of interest

@author: RWeatherl

"""

import os
import matplotlib.pyplot as plt
from matplotlib.image import imread


def combine_figures(scenarios, images, tran_folder ,png_folder, png_folder2, outputfilename):

    images_list = []

    ## user defines file path
    for sc in scenarios:
        file_path = os.path.join(mdir, sc, tran_folder, 'post_process', 'ucn2png', 'output',
                                 'png', png_folder)
        for img in images:            
            images_list.append(f'{file_path}/{png_folder2}_{img}')


<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
    fig, axs = plt.subplots(4, 4, figsize = (16,9))  ##nrows, ncols
    for i, file in enumerate(images_list):
        print(f'Reading {file}\n')
=======
    fig, axs = plt.subplots(4, 4, figsize = (14,10))  ##nrows, ncols
    for i, file in enumerate(images_list):
    print(f'Reading {file}\n)
>>>>>>> d4ac1fb... add final figs
=======
    fig, axs = plt.subplots(4, 4, figsize = (16,9))  ##nrows, ncols
    for i, file in enumerate(images_list):
        print(f'Reading {file}\n')
>>>>>>> dc8b3b3... bk
=======
    fig, axs = plt.subplots(4, 4, figsize = (16,9))  ##nrows, ncols
    for i, file in enumerate(images_list):
        print(f'Reading {file}\n')
>>>>>>> 108b6eb... resolve conflix ausdata-head
        img = plt.imread(file)
        row = i % 4 ## row index --
        col = i // 4 ## column index --
        axs[row, col].imshow(img)
        axs[row, col].axis('off')
        if row == 0:
            axs[row, col].set_title(scenarios[col])
    plt.tight_layout()
    ofile = os.path.join(os.getcwd(), 'output', 'simulated_plumes_combined', outputfilename)
    plt.savefig(ofile, dpi = 600)
    print(f'Saved {ofile}\n')
    
    # plt.show()

if __name__ == "__main__":

    cwd = os.getcwd() ##located in scripts
    mdir = os.path.join(os.path.dirname(cwd), 'mruns')
    ## user define scenarios of interest
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 108b6eb... resolve conflix ausdata-head
    list_area = ['conc_CrVI'] # 'conc_CrVI
    list_area2 = ['Conc_CrVI'] # 'conc_CrVI

    list_tran_folders = ['tran_2023to2125', ] #'tran_2023to2125_ws'
    
<<<<<<< HEAD
<<<<<<< HEAD
    

    ## user define stress period figs of interest, store in separate lists for separate figs
    sps_unc = ['Lay_max_SP_001.png', 'Lay_max_SP_120.png', 'Lay_max_SP_216.png',
               'Lay_max_SP_598.png']
               
    sps_rum = ['Lay_9_SP_001.png', 'Lay_9_SP_120.png', 'Lay_9_SP_216.png',
               'Lay_9_SP_598.png']
    
    #sps_unc = ['Lay_max_SP_001.png']
               
    #sps_rum = ['Lay_9_SP_001.png']
    
    # [01] without sources               
    scenarios = ['nfa_to2125_rr4', 'sce2a_to2125_rr1', 'sce3a_rr12_to2125', 'sce3a_rr12_to2125'] # will rm that last one manually
    for area in list_area:
        for i, tran_folder  in enumerate(list_tran_folders):
            combine_figures(scenarios, sps_unc, tran_folder, area, list_area2[i], f'unconfined_no_src_treatment_{area}_{tran_folder}.png')
            combine_figures(scenarios, sps_rum, tran_folder, area, list_area2[i] ,f'rum2_no_src_treatment_{area}_{tran_folder}.png')

    
    # [02] with sources
    list_tran_folders = ['tran_2023to2125_ws', ] #'tran_2023to2125_ws'
    scenarios = ['nfa_to2125_rr4', 'sce2a_to2125_rr1', 'sce3a_rr12_to2125','sce3a_rr12_to2125'] # for ws case
    for area in list_area:
        for i, tran_folder  in enumerate(list_tran_folders):
            combine_figures(scenarios, sps_unc, tran_folder, area, list_area2[i], f'unconfined_no_src_treatment_{area}_{tran_folder}.png')
            combine_figures(scenarios, sps_rum, tran_folder, area, list_area2[i] ,f'rum2_no_src_treatment_{area}_{tran_folder}.png')


    # [03] Compare 3a vs 4a
    tran_folder = 'tran_2023to2125'
    scenarios = ['nfa_to2125_rr4', 'sce2a_to2125_rr1', 'sce3a_rr12_to2125', 'sce4a_rr6_to2125'] 
    area2 = 'Conc_CrVI'
    area = 'conc_CrVI'
    combine_figures(scenarios, sps_rum, tran_folder, area, area2, f'rum2_no_src_treatment_3a_vs_4a_v2.png')
    combine_figures(scenarios, sps_unc, tran_folder, area, area2, f'unconfined_no_src_treatment_3a_vs4a_v2.png')

<<<<<<< HEAD
=======
=======
    list_area = ['conc_CrVI'] # 'conc_CrVI
    list_area2 = ['Conc_CrVI'] # 'conc_CrVI

<<<<<<< HEAD
>>>>>>> dc8b3b3... bk
    scenarios = ['nfa_to2125_rr4', 'sce2a_to2125_rr1', 'sce3a_rr12_to2125', 'sce4a_rr6_to2125']
=======
    list_tran_folders = ['tran_2023to2125', ] #'tran_2023to2125_ws'
=======
>>>>>>> 31e1cea3... results after revising ic conc 2022
=======
>>>>>>> 31e1cea3... results after revising ic conc 2022
    
    
>>>>>>> 6a4d50a... figs for slides

    ## user define stress period figs of interest, store in separate lists for separate figs
    sps_unc = ['Lay_max_SP_001.png', 'Lay_max_SP_120.png', 'Lay_max_SP_216.png',
               'Lay_max_SP_598.png']
               
    sps_rum = ['Lay_9_SP_001.png', 'Lay_9_SP_120.png', 'Lay_9_SP_216.png',
               'Lay_9_SP_598.png']
    
    #sps_unc = ['Lay_max_SP_001.png']
               
<<<<<<< HEAD
<<<<<<< HEAD
    combine_figures(scenarios, sps_unc, 'unconfined_no_src_treatment.png')
    combine_figures(scenarios, sps_rum, 'rum2_no_src_treatment.png')
>>>>>>> d4ac1fb... add final figs
=======
    #sps_rum = ['Lay_9_SP_001.png']              
=======
    #sps_rum = ['Lay_9_SP_001.png']
    
    # [01] without sources               
    scenarios = ['nfa_to2125_rr4', 'sce2a_to2125_rr1', 'sce3a_rr12_to2125', 'sce3a_rr12_to2125'] # will rm that last one manually
    for area in list_area:
        for i, tran_folder  in enumerate(list_tran_folders):
            combine_figures(scenarios, sps_unc, tran_folder, area, list_area2[i], f'unconfined_no_src_treatment_{area}_{tran_folder}.png')
            combine_figures(scenarios, sps_rum, tran_folder, area, list_area2[i] ,f'rum2_no_src_treatment_{area}_{tran_folder}.png')

    
    # [02] with sources
    list_tran_folders = ['tran_2023to2125_ws', ] #'tran_2023to2125_ws'
    scenarios = ['nfa_to2125_rr4', 'sce2a_to2125_rr1', 'sce3a_rr12_to2125','sce3a_rr12_to2125'] # for ws case
>>>>>>> 6a4d50a... figs for slides
    for area in list_area:
        for i, tran_folder  in enumerate(list_tran_folders):
            combine_figures(scenarios, sps_unc, tran_folder, area, list_area2[i], f'unconfined_no_src_treatment_{area}_{tran_folder}.png')
            combine_figures(scenarios, sps_rum, tran_folder, area, list_area2[i] ,f'rum2_no_src_treatment_{area}_{tran_folder}.png')
>>>>>>> dc8b3b3... bk

  

    # [03] Compare 3a vs 4a
    tran_folder = 'tran_2023to2125'
    scenarios = ['nfa_to2125_rr4', 'sce2a_to2125_rr1', 'sce3a_rr12_to2125', 'sce4a_rr6_to2125'] 
    area2 = 'Conc_CrVI'
    area = 'conc_CrVI'
    combine_figures(scenarios, sps_rum, tran_folder, area, area2, f'rum2_no_src_treatment_3a_vs_4a_v2.png')
    combine_figures(scenarios, sps_unc, tran_folder, area, area2, f'unconfined_no_src_treatment_3a_vs4a_v2.png')

=======
>>>>>>> 108b6eb... resolve conflix ausdata-head

  

    # rum_list = []
    # unc_list = []
    #
    # for sc in scenarios:
    #     file_path = os.path.join(mdir, sc, 'tran_2023to2125', 'post_process', 'ucn2png', 'output',
    #                                                    'png', 'conc_CrVI')
    #     for img in sps_rum:
    #         rum_list.append(os.path.join(file_path, img))

    # fig, axs = plt.subplots(4,3, figsize = (12,10))
    # for i, file in enumerate(rum_list):
    #     print(file)
    #     img = plt.imread(file)
    #     row = i%4
    #     col = i//4
    #     axs[row, col].imshow(img)  # Display the image on the corresponding subplot
    #     axs[row, col].axis('off')  # Turn off axis
    #     if row == 0:
    #         axs[row, col].set_title(scenarios[col])
    # plt.tight_layout()
    # plt.show()  # Show the combined figure
