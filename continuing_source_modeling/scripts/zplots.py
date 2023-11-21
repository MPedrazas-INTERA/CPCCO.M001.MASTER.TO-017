import os
import pandas as pd
import glob
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')

column = '100-H-46'
sce = 'flow_2014_Oct2023' #'sce4b_rr1_to2125'

cwd = os.path.dirname(os.getcwd())
scenario = pd.read_csv(os.path.join(cwd, sce, 'stomp', 'cr6',
                                    column, 'cr6-concs-2023.csv'), skiprows = 3, index_col = None)


calib_files = glob.glob(os.path.join(cwd, 'scenarios', 'flow_2014_2022', 'stomp', 'cr6', column, '*.csv'))

rates_raw = {f: pd.read_csv(f, skiprows = 3, index_col = None) for f in calib_files}

# years = ['2015', '2016', '2017', '2018', '2019', '2021', '2022', '2023']
years = ['2015','2023']

rates=dict(zip(years,list(rates_raw.values())))

fig, ax = plt.subplots()
for k in rates_raw.keys():
    ax.set_ylim(rates_raw[k].iloc[-1,5], rates_raw[k].iloc[0,5])
    ax.plot(rates_raw[k].iloc[:,19], rates_raw[k].iloc[:,5])
    ax.grid(True)
    ax.legend(years)
    # ax.set_xlabel('Aqueous cr6 (mol/m3)')
    plt.title(f'{column}')
    # plt.savefig(os.path.join(os.getcwd(), 'output', f'calibration_run_2015_2023_{column}.png'))

calib = rates['2023']
fig, ax = plt.subplots()
ax.plot(calib.iloc[:,16], calib.iloc[:,5], color = 'grey', label = 'Calibration - 2023')
ax.plot(scenario.iloc[:,16], scenario.iloc[:,5], color = 'blue', linestyle='dotted', label = 'Predictive - 2023')
ax.set_ylim(rates_raw[k].iloc[-1,5], rates_raw[k].iloc[0,5])
ax.grid(True)
ax.legend()
ax.set_xlabel('Aqueous cr6 (mol/m3)')
plt.title(f'{column}')
plt.savefig(os.path.join(os.getcwd(), 'output', f'calibration_vs_predictive_{column}_2023.png'))