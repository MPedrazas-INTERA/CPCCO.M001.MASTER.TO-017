import os
import pandas as pd
import glob
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use('Qt5Agg')

column = '100-H-46'
sce = 'flow_2014_Oct2023'

cwd = os.path.dirname(os.getcwd())

def plot_multiple_years():

    calib_files = glob.glob(os.path.join(cwd, 'flow_2014_Oct2023', 'stomp', 'cr6', column, '*.csv'))
    rates_raw = {f: pd.read_csv(f, skiprows = 3, index_col = None) for f in calib_files}
    years = ['2015', '2016', '2017', '2018', '2019', '2021', '2022', '2023']
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

    # scenario = pd.read_csv(os.path.join(cwd, sce, 'stomp', 'cr6',
    #                                     column, 'cr6-concs-100D562-2023.csv'), skiprows = 3, index_col = None)

    # calib = rates['2023']
    # fig, ax = plt.subplots()
    # ax.plot(calib.iloc[:,16], calib.iloc[:,5], color = 'grey', label = 'Calibration - 2023')
    # ax.plot(scenario.iloc[:,16], scenario.iloc[:,5], color = 'blue', linestyle='dotted', label = 'Predictive - 2023')
    # ax.set_ylim(rates_raw[k].iloc[-1,5], rates_raw[k].iloc[0,5])
    # ax.grid(True)
    # ax.legend()
    # ax.set_xlabel('Aqueous cr6 (mol/m3)')
    # plt.title(f'{column}')
    # plt.savefig(os.path.join(os.getcwd(), 'output', f'calibration_vs_predictive_{column}_2023.png'))

    return None

def plot_one_year():
#%%
    rates_raw = pd.read_csv(
        os.path.join(cwd, sce, 'stomp', 'cr6', column, 'cr6-concs-2023.csv'), skiprows=3,
        index_col=None)
    years = ['2023']

    fig, ax = plt.subplots()
    ax.set_ylim(rates_raw.iloc[0,5],rates_raw.iloc[-1,5])
    ax.plot(rates_raw.iloc[:,16], rates_raw.iloc[:,5])
    ax.grid(True)
    ax.legend(years)
    ax.set_xlabel('Aqueous cr6 (mol/m3)')
    ax.set_ylabel('Elevation (m)')
    plt.title(f'{column}')
    plt.show()
#%%
    return None

if __name__ == '__main__':

    plot_one_year()