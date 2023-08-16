import pandas as pd 
import geopandas as gpd


'''
hpham@intera.com, 02/16/2023
- Run py03_ras2ref_4ghb.py
- Run process_GHB_export_from_GMS.py

Assign water levels to GHB cells (no changes in GHB conductance)

NOT USE THIS SCRIPT ANYMORE.
USE py03_ras2ref_4ghb.py

'''

wdir = f'../model_packages/hist_2014_2021/ghb/'
ifile = f'{wdir}/Shapefile/GHB_Lay6.shp'
ofile = f'{wdir}/Shapefile/GHB_CY2022_v021623.shp'
ofile2 = f'{wdir}/Shapefile/GHB_CY2022_v021623.csv'

col_2021 = [f'head{i}' for i in range(last_sp+1, last_sp+ n_new_sp+1,1)]
col_2022 = [f'head{i}' for i in range(last_sp+1+12, last_sp+ n_new_sp+1+12,1)]
dict_col = dict(zip(col_2021, col_2022))
head_north_ghb = 120

gdf = gpd.read_file(ifile)
gdf.head()
ghb_cells = gdf[['row', 'column']]
last_sp = 180
n_new_sp = 12 # 12 new sp for cy 2021
yr=2020
# combine monthly rs from 12 csv files (for 12 months in 2021)
for i in range(n_new_sp):
    ifile2 = f'{wdir}/raster_files/interpolated_wl_yr{yr}mo{i+1}.csv'
    print(i+1,ifile2)
    df=pd.read_csv(ifile2)
    if i==0:
        interpolated_wl=df.copy()
        interpolated_wl.rename(columns={'val':f'head{last_sp+i+1}'}, inplace=True)
    else:
        interpolated_wl[f'head{last_sp+i+1}'] = df['val']

# rename
interpolated_wl.rename(columns={'I':'row', 'J':'column'}, inplace=True)


# combine
interpolated_wl_merged = pd.merge(interpolated_wl,ghb_cells, how='right', on=['row','column'])
for col in col_2021:
    interpolated_wl_merged[col].loc[interpolated_wl_merged['row']!=433] = head_north_ghb

# dupplicate 2021 to make 2022 (while waiting for 2022 interpolated WLs)


interpolated_wl_2022 = interpolated_wl_merged.copy()
interpolated_wl_2022.rename(columns=dict_col, inplace=True)



gdf = pd.concat([gdf, interpolated_wl_merged[col_2021],interpolated_wl_2022[col_2022]], axis=1)
#gdf.columns
gdf.plot(figsize=(12,10))
gdf['cell_id'] =  'row' + gdf['row'].astype('str') + 'col' + gdf['column'].astype('str')
'row433col685'

col_out =['cell_id'] + [f'head{i}' for i in range(1, last_sp+ n_new_sp*2+1,1)]

gdf2 = gdf[gdf['row']== 433]

# Save to file
gdf.to_file(ofile)
print(gdf.head())
print(f'\nSaved {ofile}\n')

gdf2[col_out].to_csv(ofile2, index=False)

