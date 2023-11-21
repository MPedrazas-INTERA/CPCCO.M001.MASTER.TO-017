~Simulation Title Card
1,
Waste Site 100-D-100 Slope Cr6,
R Weatherl,
Intera Inc.,
November 21, 2023,
10:00 CST,
2,
Derivation of a characteristic breakthrough curve for waste sites in 100-HR-3 Groundwater OU with STOMP Version 4.0.
The breakthrough curve will be used to develop a continuing source (SSM package) for MT3D.
#######################
~Solution Control Card
restart file, ./ss_flow/restart,
Water w/ ECKEChem w/ courant,1.0,
1,
2014.,yr,2023.833,yr,1.0e-06,d,1,d,1.25,8,1.e-6,
500000000,
0,
########################
### Representative soil column 2 (developed by Terry Tolan) provided HSU thickness 
### as BGS. Therefore, these values were converted to elevation above NAVD88 datum
### Average disk Z of wells D5-97, D5-146, D5-122, D5-102, D5-99, D5-144, D5-119, D5-103
### is about 143.5 m.
### 23.5 m Hanford and 10.1 m Ringold E
### The vadose zone thickness in the representative columns does not include the excavation.
### Excavation should be considered if there is significant reduction in vadose
### zone thickness.  
~Grid Card
cartesian,
1,1,         121,
# X Direction, nodes
0.0,m,10.0,m,
# Y Direction (Not Used)
0.,m,10.0,m,
# Z Direction nodes run for 100-HR-3
#Need a better estimate from model output
#Water Table Elevation = 118.25 average WT (Min WT = 117.64 m and Max WT = 119.48 m)
#bottom node center = 113.375 m
113.25,m,         121@0.25,m,
########################
~Rock/Soil Zonation Card
#
3,
RS,1,1,1,1,1,        20,
RE,1,1,1,1,        21,        27,
HF,1,1,1,1,        28,        121,
########################
~Mechanical Properties Card
#Soil name,particle density,units,total porosity,diffusive porosity (theta S),specific storativity - default = 1E-07*diff porosity,
#units - default = 1/m, tortuosity function,
#BF,2.68,g/cm^3,0.276,0.262,Pore Compressibility,1e-7,1/Pa,,,Millington and Quirk, # ECF-200MW1-10-0080 Table 6
HF,2.68,g/cm^3,0.114,0.114,Pore Compressibility,1e-7,1/Pa,,,Millington and Quirk, # density ECF-200MW1-10-0080 Table 6; porosity from average of samples 2-1318, and 3-1702 in table 6 (ECF-HANFORD-11-0063),
RE,2.68,g/cm^3,0.178,0.178,Pore Compressibility,1e-7,1/Pa,,,Millington and Quirk, # density ECF-200MW1-10-0080 Table 6; porosity from average of samples 2-1307, and 2-1308 in table 6 (ECF-HANFORD-11-0063),
RS,2.68,g/cm^3,0.178,0.178,Pore Compressibility,1e-7,1/Pa,,,Millington and Quirk, # density ECF-200MW1-10-0080 Table 6; porosity from average of samples 2-1307, and 2-1308 in table 6 (ECF-HANFORD-11-0063),,
#

~Hydraulic Properties Card
#Soil name, x-direction hydraulic conductivity, units, y-direction hydraulic conductivity (not used),
#units, z-direction hydraulic conductivity, units,
#BF,5.98E-04,hc:cm/s,,,5.98E-04,hc:cm/s, # ECF-Hanford-11-0063-r6 Table 7
HF,4.66E-03,hc:cm/s,,,4.66E-04,hc:cm/s, # ECF-Hanford-11-0063-r6 Table 7
RE,9.48E-04,hc:cm/s,,,9.48E-05,hc:cm/s, # ECF-Hanford-11-0063-r6 Table 7
RS,2.59E-02,hc:cm/s,,,2.59E-03,hc:cm/s, # ECF-Hanford-11-0063-r6 Table 7
#

~Saturation Function Card
#Soil name, moisture retention function, vG alpha, units, vG n, residual saturation, vG m - default = 1 - 1/n
#BF,Nonhysteretic van Genuchten,0.019, 1/cm,1.4,0.103,, # # ECF-Hanford-11-0063-r6 Table 7 (ECF-HANFORD-15-0129 documented wrong Sr value)
HF,Nonhysteretic van Genuchten,0.029, 1/cm,1.378,0.0474,, # Table 7 in ECF-HANFORD-11-0063, Sr calculated from average theta-r (0.0108,0) and average porosity 0.114
RE,Nonhysteretic van Genuchten,0.013, 1/cm,1.538,0.0834,, # Table 7 in ECF-HANFORD-11-0063, Sr calculated from average theta-r (0.0089, 0.0208) and average porosity 0.178
RS,Nonhysteretic van Genuchten,0.013, 1/cm,1.538,0.0834,, # Table 7 in ECF-HANFORD-11-0063, Sr calculated from average theta-r (0.0089, 0.0208) and average porosity 0.178

########################
## Excavation slope ranges 127.5 to 140 m within slope. Using source up to 50% of (135 m -118.25 m) = 34 cells 
~Initial Conditions Card
Aqueous Pressure,Gas Pressure,
5,
Overwrite Species Volumetric,Cr6(ads),0,mol/m^3,,,,,,,1,1,1,1,1,20,
Overwrite Species Volumetric,Cr6(ads),0.0113,mol/m^3,,,,,,,1,1,1,1,21,54,
Overwrite Species Volumetric,Cr6(ads),0.0,mol/m^3,,,,,,,1,1,1,1,55,71,
Overwrite Species Volumetric,Cr6(ads),0.0,mol/m^3,,,,,,,1,1,1,1,72,103,
Overwrite Species Volumetric,Cr6(ads),0,mol/m^3,,,,,,,1,1,1,1,104,121,
########################
~Aqueous Relative Permeability Card
#BF,Mualem,,
HF,Mualem,,
RE,Mualem,,
RS,Mualem,,
########################
~Solute/Porous Media Interaction Card
#BF,0.0,m,0.0,m,
HF,0.0,m,0.0,m,
RE,0.0,m,0.0,m,
RS,0.0,m,0.0,m,
#########################
~Aqueous Species Card
1,Constant,1.e-9, cm^2/s, B-dot,
cr6,2,3.0,A,116.0,kg/kmol,
#########################
~Solid Species Card
1,
cr6(ads),,,52.0,kg/kmol,
#########################
~Kinetic Reactions Card
1,
KnRc-1, Valocchi Sorption,1,cr6,1.0,1,cr6(ads),1.0,
#From Sunil's Email; STOMP_Modeling_Kinetic_Rate_Cr.xlsx; ECF-100BC5-16-0028-r0.pdf
1E-4,1/hr,0.15,mL/g,
#########################
~Kinetic Equations Card
1,
Kinetic_Cr6(ads),1,cr6(ads),1.0,
1,KnRc-1,1.0,
##########################
~Conservation Equations Cards
1,
Total_cr6,2,cr6,0.100E+01,cr6(ads),0.100E+01,
###########################
~Boundary Conditions Card
3,
top,neumann,species zero flux,
0,
1,1,1,1,121,121,2,
2012.0,yr,-46.00000000,mm/yr,,,,,,,,,,,
2023.0,yr,-46.00000000,mm/yr,,,,,,,,,,,
###
west,hydraulic gradient, outflow,
0,
1,1,1,1,1, 24,119,
|up_gradient_cell|
############################################
east,hydraulic gradient, outflow,
0,
1,1,1,1,1, 24,119,
|down_gradient_cell|
###################################
~Surface Flux Card
8,
2,gw_conc_16-24.srf,
Aqueous Volumetric Flux,m^3/yr,m^3,east,1,1,1,1,         16,        24,
Conservation Component Mass Flux,Total_cr6,mol/yr,mol,east,1,1,1,1,         16,        24,
2,gw_conc_10-24.srf,
Aqueous Volumetric Flux,m^3/yr,m^3,east,1,1,1,1,         10,        24,
Conservation Component Mass Flux,Total_cr6,mol/yr,mol,east,1,1,1,1,         10,        24,
2,gw_conc_1-24_east.srf,
Aqueous Volumetric Flux,m^3/yr,m^3,east,1,1,1,1,         1,        24,
Conservation Component Mass Flux,Total_cr6,mol/yr,mol,east,1,1,1,1,         1,        24,
2,gw_conc_1-24_west.srf,
Aqueous Volumetric Flux,m^3/yr,m^3,west,1,1,1,1,         1,        24,
Conservation Component Mass Flux,Total_cr6,mol/yr,mol,west,1,1,1,1,         1,        24,
############################################
~Output Control Card
10,
1,1,        15,
1,1,        16,
1,1,        17,
1,1,        18,
1,1,        19,
1,1,        20,
1,1,        21,
1,1,        22,
1,1,        23,
1,1,        24,
#
2,1,yr,m,3,12,12,
15,
rock/soil type,,
Integrated Water Mass, kg,
aqueous saturation,,
aqueous pressure,pa,
aqueous hydraulic head,m,
aqueous moisture content,,
xnc aqueous vol,mm/yr,
ync aqueous vol,mm/yr,
znc aqueous vol,mm/yr,
matric potential,cm,
species integrated mass,total_cr6,,
species aqueous concentration,cr6,,
species volumetric concentration,cr6,,
species aqueous concentration,cr6(ads),,
species volumetric concentration,cr6(ads),,
#
9,
2014.000000,yr,
2015.000000,yr,
2016.000000,yr,
2017.000000,yr,
2018.000000,yr,
2019.000000,yr,
2021.000000,yr,
2022.000000,yr,
2023.581000,yr,
14,
rock/soil type,,
aqueous saturation,,
aqueous pressure,pa,
aqueous hydraulic head,m,
aqueous moisture content,,
xnc aqueous vol,mm/yr,
ync aqueous vol,mm/yr,
znc aqueous vol,mm/yr,
matric potential,cm,
species aqueous concentration,cr6,,
species volumetric concentration,cr6,,
species aqueous concentration,cr6(ads),,
species volumetric concentration,cr6(ads),,
final restart,,