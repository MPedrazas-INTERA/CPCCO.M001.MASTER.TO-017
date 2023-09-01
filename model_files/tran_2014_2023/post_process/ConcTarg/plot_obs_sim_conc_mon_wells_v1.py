# -*- coding: utf-8 -*-
"""
Created on Thu Feb  3 14:53:14 2022

INPUT:              time series of observed and simulated concentration at monitoring wells
                        conc-targsCTET_600.out (from script/executable)
                        conc-targsNitrate.out  (from script/esecutable) 
                    well_toplot.csv - list of wells to plot by COC
CALCULATIONS:       use input values of days elpased since 01/01/2015 to calculate calendar date
OUTPUT:             plots of obs vs simulated concentration from 1/1/2015 to 12/31/2020
                    ./images/<COC>_<0#>.png
                    
COMMENT:   
                I applied a uniform scale for nitrate of 10^3 to 10^6 µg/L but
                    - well 299-W19-43 has a higher observed concentration which is truncated on the plot
                    - well 299-W22-24P has a lower observec concentration which is truncated on the plot

@author: jblainey
"""
import pandas as pd
import os
import platform
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import datetime
import matplotlib.dates as mdates
import matplotlib.patches as patches

print('python version: {}'.format(platform.python_version()))   # 3.9.0
print('pandas version: {}'.format(pd.__version__))              # 1.1.3
print('numpy version: {}'.format(np.__version__))               # 1.19.2
print('matplotlib version: {}'.format(mpl.__version__))         # 3.3.2

#%% Variables
syear=2015
eyear=2022
coc=['ctet','no3']
#coc=['ctet']
ifnam={'ctet': 'conc-targs_CY2022_CTET_600.out', 'no3': 'conc-targs_CY2022_Nitrate.out'}
unit={'ctet': '\u03BCg/L', 'no3':'\u03BCg/L'}       #micrograms
suptitle={'ctet': 'Carbon Tetrachloride','no3': 'Nitrate'}
myylim={'ctet':[0.1,3000],'no3':[910,1000000]}    
#%% Read Inputs
dfw=pd.read_csv('well_toplot.csv')              # read list of wells to plot
# read concentration time series obs and sim
df=pd.DataFrame()
for c in coc:                                 
    df0=pd.read_csv(ifnam[c], skiprows=1, sep='\s+' )
    df0['coc']=c
    df=df.append(df0, ignore_index=True)
df['sDate']=datetime.date(syear,1,1)
df['Date']=df[['sDate','time']].apply(lambda x: x['sDate']+pd.DateOffset(days=x['time']-1.0), axis=1)
#%% Plot https://engineeringfordatascience.com/posts/matplotlib_subplots/
if not os.path.exists('images'):
    os.makedirs('images')
nr=3
nc=4
for c in coc:
    tickers=sorted(dfw[dfw['coc']==c].well.tolist())
    # loop for pages, and wells per page, change start in enumerate
    npg=-(-len(tickers)//(nr*nc))             #round up without math functions https://stackoverflow.com/questions/2356501/how-do-you-round-up-a-number
    for p in range(0,npg):
#    for p in range(0,1):
        ls=0+p*nr*nc
        le=min(nr*nc-1+ls,len(tickers)-1)
        print(c, 'page', p)
#        print(p,ls,le)
#        print(p,tickers[ls],tickers[le])
        plt.figure(figsize=(9*1.5,6.5*1.4))   
        plt.suptitle(suptitle[c], fontsize=18, y=0.95)
        for n, ticker in enumerate(tickers[ls:le+1]):
            ax=plt.subplot(nr,nc,n+1)
            # filter df and ticker on new plot
            df[(df['coc']==c) & (df['obsname']==ticker)].plot(x='Date', y='measured', ax=ax, marker='o', linestyle='None', legend=None)
            df[(df['coc']==c) & (df['obsname']==ticker)].plot(x='Date', y='modeled', ax=ax, marker='None', legend=None)
            # chart formatting
            ax.set_title(ticker)
            ax.set_xlim([datetime.date(syear, 1, 1), datetime.date(eyear+1, 1, 1)])
            ax.set_xlabel(None)
            ax.xaxis.set_major_locator(mdates.YearLocator(1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
            # for label in ax.get_xticklabels(which='major'): 
            #     print(label)
            #     label.set(rotation=0, horizontalalignment='center')
            ax.set_ylabel('Concentration ({})'.format(unit[c]))
            ax.set_yscale('log')
            ax.set_ylim(myylim[c])
            ax.tick_params(direction='in')
            ax.yaxis.grid(which='major')
            if c=='no3': 
                ax.yaxis.grid(which='minor', linestyle='--', dashes=(5,60))
            if(n==0): 
                handles, labels = ax.get_legend_handles_labels()
                ax.legend(labels=['Observed', 'Simulated'], bbox_to_anchor=(1.25, 1.35), ncol=2)
        plt.tight_layout()
        plt.subplots_adjust(hspace=0.3, wspace=0.3)
        plt.savefig(os.path.join(os.getcwd(),'images', str(c) + '_'+ str(p).zfill(2) + '.png'))
        plt.close() 
        
        
#%% Plot monitorin wells 299-W18-21, 299-W18-22, and 299-W6-6 for the 200 Areas P&T Report 
#   Similar to Figure 3-3 in DOE/RL-2020-62 Rev 0, observed and simulated
#https://www.tutorialspoint.com/overlapping-y-axis-tick-label-and-x-axis-tick-label-in-matplotlib
#https://stackoverflow.com/questions/2027592/draw-a-border-around-subplots-in-matplotlib

mywells=['299-W18-21', '299-W18-22', '299-W6-6']
myymax={'299-W18-21': [0,140000], '299-W18-22':[0,35000], '299-W6-6': [0,140000]}

nr=3
nc=1
tickers=mywells
ls=0
le=min(nr*nc-1+ls,len(tickers)-1)
fig=plt.figure(figsize=(5*1.4,9*1.5))   
#plt.suptitle(suptitle[c], fontsize=18, y=0.95)
for n, ticker in enumerate(tickers[ls:le+1]):
    ax=plt.subplot(nr,nc,n+1)
    # filter df and ticker on new plot
    df[(df['coc']=='no3') & (df['obsname']==ticker)].plot(x='Date', y='measured', ax=ax, marker='o', linestyle='None', legend=None)
    df[(df['coc']=='no3') & (df['obsname']==ticker)].plot(x='Date', y='modeled', ax=ax, legend=None)
    # chart formatting
    ax.set_title(ticker + '\n ', fontsize=18)
    ax.set_xlim([datetime.date(syear, 1, 1), datetime.date(eyear+1, 1, 1)])
    ax.set_xlabel(None)
    ax.xaxis.set_major_locator(mdates.YearLocator(1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    
    for label in ax.get_xticklabels(which='major'): 
        label.set(rotation=0, horizontalalignment='center', fontsize=14)
               
    ax.tick_params(axis='y', labelsize=14)
    ax.set_ylabel('Concentration ({})'.format(unit[c]), fontsize=12)
    ax.set_ylim(myymax[ticker])
    ax.tick_params(direction='in')
    ax.xaxis.grid(which='major')
    ax.yaxis.grid(which='major') 
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(labels=['Measured', 'Simulated'], bbox_to_anchor=(0.8, 1.12), ncol=2, fontsize=14, frameon=False)

    # add border around subplots,  rect = plt.Rectangle(#(lower-left corner), width, height
    rect = plt.Rectangle((0.0, 0.67), 1, 0.33, fill=False, color="k", lw=1.25, zorder=1000, transform=fig.transFigure, figure=fig)  #subplot 0
    fig.patches.extend([rect])
    rect = plt.Rectangle((0.0, 0.67/2.0), 1, 0.33, fill=False, color="k", lw=1.25, zorder=1000, transform=fig.transFigure, figure=fig) #subplot 1
    fig.patches.extend([rect])           
    rect = plt.Rectangle((0.0, 0.0), 1, 0.33, fill=False, color="k", lw=1.25, zorder=1000, transform=fig.transFigure, figure=fig)  #subplot 2
    fig.patches.extend([rect])


plt.tight_layout()
plt.subplots_adjust(hspace=0.3, wspace=0)
plt.margins(x=0, y=0)
plt.savefig(os.path.join(os.getcwd(),'images', 'no3_obssim3wells_Fig3-3.png'))
plt.close() 
