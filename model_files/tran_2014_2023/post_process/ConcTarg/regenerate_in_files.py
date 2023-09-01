import pandas as pd 

   

if __name__ == "__main__":
    dic_chem = {'CTET':'conc-targs_CY2022_CTET_600.in', 'Nitrate':'conc-targs_CY2022_Nitrate.in'}
    dic_ucn = {'CTET':'..\\CTET_600y\P2Rv8.3_CTET_600y.UCN', 'Nitrate':'..\\Nitrate\\Nitrate.UCN'}
    last_acc_days = 2953 # days, to extract data
    

    for chem in dic_chem.keys():
        # readin the timestep and daes
        df_time = pd.read_csv(f'timesteps_{chem}.csv')      
        df_time=df_time[df_time['Time']<=last_acc_days] 
        
        # readin the current *.in file for "ConcTarg2.exe" run        
        col_names = ['SSPA_Well_ID','Time','loc_x','loc_y','MidScreenElev(ft)','SSPA_Value']
        df_in = pd.read_csv(dic_chem[chem], skiprows=11, delim_whitespace=True, names=col_names)
        list_wells = df_in['SSPA_Well_ID'].unique()

        df_final=pd.DataFrame()
        for wname in list_wells:
            df_in2 = df_in[df_in['SSPA_Well_ID']==wname]
            df_in2=df_in2.reset_index(drop=True)

            # 
            df_time['SSPA_Well_ID']= wname
            df_time['loc_x'] = df_in2['loc_x'].iloc[0]
            df_time['loc_y'] = df_in2['loc_y'].iloc[0]
            df_time['MidScreenElev(ft)'] = df_in2['MidScreenElev(ft)'].iloc[0]
            df_time['SSPA_Value'] = -999 #float('nan')
            

            
            # Merge two dataframes: df_time and df_in2
            df_merge = pd.merge(df_time, df_in2, how='outer', on=col_names)

            df_final=pd.concat([df_final, df_merge])

        # sort df_final by Time to match requirement of  ConTarg2.exe 
        df_final.sort_values(by='Time', ascending=True, inplace=True)

        # Write to file
        ofile = f'{dic_chem[chem]}2'
        fid = open(ofile, 'w')
        fid.write(f'#Headtarg.exe input file\n')
        fid.write(f'NTARG	{df_final.shape[0]}\n')
        fid.write(f'DISFILE	..\SharedFiles\P2R_Vistas_flow_sp2022.dis\n')
        fid.write(f'XOFF	557800\n')
        fid.write(f'YOFF	116200\n')
        fid.write(f'ROTATION	0\n')
        fid.write(f'CONCFILE	{dic_ucn[chem]}\n')
        fid.write(f'CUTOFF	0.000000001\n')
        fid.write(f'LOGLIN	lin\n')
        fid.write(f'#End In\n')
        fid.write(f'#SSPA_Well_ID	Time	loc_x	loc_y	MidScreenElev(ft)	SSPA_Value\n')
        fid.close()

        # reorder columns
        df_final[col_names].to_csv(ofile, mode='a', header=False, index=False, sep='\t')
    



    


