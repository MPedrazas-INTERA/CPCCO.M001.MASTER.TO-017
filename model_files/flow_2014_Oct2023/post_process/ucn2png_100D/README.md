# ucn2png
Convert MODFLOW MT3D UCN file to png and shapefile using flopy and GeoPandas by hpham@intera.com
Last updated: 03/15/2022

INSTALLATION Python Environment using Anaconda
1. Download Anaconda Individual Edition https://repo.anaconda.com/archive/Anaconda3-2021.11-Windows-x86_64.exe
2. Install Anaconda to your Windows PC
3. Setup a new conda environment
- Open Anaconda Prompt (Anaconda3)
- Check list of current conda environments installed in your PC: conda env list
- Install a new conda environment: conda create -n flopy python=3
- Activate the just created conda environment: conda activate flopy
- Install some libraries needed for the script (all libs at once to avoid conflict):
   conda install -c conda-forge flopy geopandas numpy matplotlib pandas
4. Or you can install a new conda env using flopy.yml included in this repo:
   conda env create -f flopy.yml
   
CLONE THIS REPO:
   git clone https://github.com/HPham-INTERA/ucn2png.git   
   
RUN SCRIPT
   - Prepare input file in input/input.csv. Remember to modify path to UCN file and basemap files. 
   - Open program "Anaconda Prompt (Anaconda3)"
   - Activate flopy conda env: conda activate flopy OR source activate b3
   - Go to folder ucn2png
   - Run this command to amke PNGs: python main.py Rebound input/input_100H.csv Y 1 118 1
   - Make GIFs with PNGs: python plume_map_GIFs_linux.py


