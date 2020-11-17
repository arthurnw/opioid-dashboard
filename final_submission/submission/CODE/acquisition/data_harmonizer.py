
import pandas as pd
import numpy as np

# Additional packages we may need but aren't being used currently
'''
import re
import json
import csv
from pprint import pprint
import os
import sys
'''

# --------------------------------------------------------------------------------
## Toggles

# Enable more logging
debug = True



# --------------------------------------------------------------------------------
## Parameters

# Where to read / write the data
dataRawDir      = "data_raw/"                               # Folder where the raw data sets are located
dataCleanDir    = "data_clean/"                             # Folder to place the cleaned up data files

# Input Files
#cdcDataFile     = "ALL_US_6yr.tab"                          # CDC UCD / MCD data, source: CDC wonder
cdcDataFile     = "ALL_US_6yr_adj.tab"                      # CDC UCD / MCD data, source: CDC wonder
cdcState00File  = "cdc_state_2000.txt"                      # CDC UCD / MCD data, source: CDC wonder
cdcState10File  = "cdc_state_2010.txt"                      # CDC UCD / MCD data, source: CDC wonder
cdcState17File  = "cdc_state_2017.txt"                      # CDC UCD / MCD data, source: CDC wonder
countyFile      = "2018_Gaz_counties_national.txt"          # FIPs, Lat / Lon, source: census.gov gazetteer files
statePopFile    = "state_pops.csv"                          # State Population by year
edu0017File     = "Education.xls"                           # Education by county, 2000 and 2017
edu2009bFile    = "edu_bachelors_2009.csv"                  # Education by county, bachelors 2009
edu2009hFile    = "edu_high_school_2009.csv"                # Education by county, high school 2009
pov00File       = "poverty_and_income_2000.csv"             # Poverty estimates by county - 2000
pov09File       = "poverty_2009.csv"                        # Poverty estimates by county - 2009
pov17File       = "poverty_2017.csv"                        # Poverty estimates by county - 2017
medHH09File     = "median_household_income_2009.csv"        # Media Household Income - 2009
medHH17File     = "median_household_income_2017.csv"        # Media Household Income - 2017
labor00File     = "labor_2000.xlsx"                         # Unemployment by county - 2000
labor09File     = "labor_2009.xlsx"                         # Unemployment by county - 2009
labor17File     = "labor_2017.xlsx"                         # Unemployment by county - 2017
demo0003aFile   = "demographics_2003a.csv"                  # Demographics for 2000 - 2003 (First half)
demo0003bFile   = "demographics_2003b.csv"                  # Demographics for 2000 - 2003 (Second half)
demo1018File    = "demographics_2010_2018.csv"              # Demographics for 2010 - 2018

# Prediction Files - output of Prediction script
deathRateFile   = "predicted_death_rate.csv"                # Predicted Mean Deaths per 100k - 2024
deathAdjFile    = "predicted_deaths_age_adj.csv"            # Predicted Age Adjusted Death Rate - 2024

# Output Files
cdcOut          = "cdc.tab"                                 # Output for cleaned up CDC wonder data
countyOut       = "county_latlon.tab"                       # Output for cleaned up countyLatLon file
predInputOut    = "prediction_input.tab"                    # Input file for the prediction
mapOut          = "map_input.tab"                           # Input file for the choropleth
predictMapOut   = "prediction_map_input.tab"                # Input file for the choropleth - prediction screen
subOut          = "subplot_input.tab"                       # Input file for investigation subplots

if debug :
    print()
    print("DATA SET FILES\n")
    print("\tData Set\tInput File\t\t\t\tCleaned File")
    print("\t---------------------------------------------------------------------------")
    print("\tCDC County\t"+cdcDataFile+"\t\t\t"+cdcOut)
    print("\tCDC State 00\t"+cdcState00File+"\t\t\t"+cdcOut)
    print("\tCDC State 10\t"+cdcState10File+"\t\t\t"+cdcOut)
    print("\tCDC State 17\t"+cdcState17File+"\t\t\t"+cdcOut)
    print("\tState Pops\t"+statePopFile+"\t\t\t"+cdcOut)
    print("\tCounties\t"+countyFile+"\t\t"+countyOut)
    print("\tEdu 2000/17\t"+edu0017File+"\t\t")
    print("\tEdu 2009 hs\t"+edu2009hFile+"\t\t")
    print("\tEdu 2009 bs\t"+edu2009bFile+"\t\t")
    print("\tPoverty 00\t"+pov00File+"\t\t")
    print("\tPoverty 09\t"+pov09File+"\t\t")
    print("\tPoverty 17\t"+pov17File+"\t\t")
    print("\tMed HH 09\t"+medHH09File+"\t\t")
    print("\tMed HH 17\t"+medHH17File+"\t\t")
    print("\tLabor00\t\t"+labor00File+"\t\t")
    print("\tLabor09\t\t"+labor09File+"\t\t")
    print("\tLabor17\t\t"+labor17File+"\t\t")
    print("\tDemo '00 '03 a\t"+demo0003aFile+"\t\t")
    print("\tDemo '00 '03 b\t"+demo0003bFile+"\t\t")
    print("\tDemo '10 '18\t"+demo1018File+"\t\t")
    print("\t---------------------------------------------------------------------------")
    print()

# --------------------------------------------------------------------------------
## Functions

def stripWhiteSpace(df) :
    '''
    Takes in a dataframe and trims whitespace on str columns and the header
    '''
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.columns = df.columns.map(lambda x: x.strip()).str.lower().str.replace(', ',',').str.replace(' ','_').str.replace("-","_").str.replace("'","")

    return df

def openTabFile(file) :
    '''
    Takes in a tab file, opens it into a dataframe, trims, and returns it
    '''
    df = pd.read_csv(dataRawDir+file, sep='\t', dtype=str)
    return stripWhiteSpace(df)

def openCsvFile(file) :
    '''
    Takes in a csv file, opens it into a dataframe, trims, and returns it
    '''
    df = pd.read_csv(dataRawDir+file, encoding='ISO-8859-1', sep=',', dtype=str)
    return stripWhiteSpace(df)

def openXlsFile(file, sheet, skip) :
    '''
    Takes in an excel file, opens it into a dataframe, trims, and returns it
    '''
    df = pd.read_excel(dataRawDir+file,sheet_name=sheet, skiprows=skip, dtype=str)
    return stripWhiteSpace(df)

def writeTabFile(df, filename) :
    '''
    Takes in a dataframe and a filename and outputs the dataframe to a tab delimited file
    '''
    df.to_csv(dataCleanDir+filename, sep='\t', encoding='utf-8', index=False)

# --------------------------------------------------------------------------------
## Process CDC / MCD Data

# Load file into DataFrame
cdcData = openTabFile(cdcDataFile)

# Clean up years, get min and max year for each row
years = cdcData['year'].str.split(",").apply(pd.Series).astype(int) 
cdcData['year_min'], cdcData['year_max'] = years.min(axis=1), years.max(axis=1)
cdcData['year'] = cdcData['year'].str.split(',')

# Fields to Rename
cdcColsToRename = { 'year'              : 'year_list',
                    'county_code'       : 'fips',
                    'age_adjusted_rate' : 'deaths_age_adj'
                  }

# Rename Fields
cdcData = cdcData.rename(columns=cdcColsToRename)

#cdcData['year'] = cdcData['year_min']
cdc_yr_conditions = [
    cdcData['year_min'] == 2000,
    cdcData['year_min'] == 2006,
    cdcData['year_min'] == 2012
]

# Add the "representative year" - mostly used for joining
cdc_yr_map = ['2000','2010','2017']
cdcData['year'] = np.select(cdc_yr_conditions, cdc_yr_map)

# List fields we want to keep
cdcColsToKeep = [   'county',
                    'state',
                    'fips',
                    'state_code',
                    'deaths',
                    'deaths_age_adj',
                    'crude_rate',
                    'year',
                    'year_min',
                    'year_max',
                    'year_list'
                ]

# Grab the columns we want
cdcData = cdcData[cdcColsToKeep]

if debug: 
    print()
    print("CDC File:\n")
    print(cdcData.head())
    print()


# Write cleaned-up file
writeTabFile(cdcData, cdcOut)

# --------------------------------------------------------------------------------
## Process Education data

# Read in the 2009 HS Education File
edu2009hData = openCsvFile(edu2009hFile)
edu2009hHeaders = edu2009hData.iloc[0]
edu2009hData  = pd.DataFrame(edu2009hData.values[1:], columns=edu2009hHeaders)
edu2009hData = stripWhiteSpace(edu2009hData)

edu2009hData = edu2009hData[(edu2009hData['target_geo_id2'] != '01') & (edu2009hData['target_geo_id2'].notnull()) ]

edu2009hColsToRename =  {   'target_geo_id2'    : 'fips',
                            'percent'           : 'pct_hs_diploma'
                        }
edu2009hData = edu2009hData.rename(columns=edu2009hColsToRename)

edu2009hData['year'] = "2010"
edu2009hData = edu2009hData[['fips', 'year', 'pct_hs_diploma']]

# Read in the 2009 BS Education File
edu2009bData = openCsvFile(edu2009bFile)
edu2009bHeaders = edu2009bData.iloc[0]
edu2009bData  = pd.DataFrame(edu2009bData.values[1:], columns=edu2009bHeaders)
edu2009bData = stripWhiteSpace(edu2009bData)

edu2009bData = edu2009bData[(edu2009bData['target_geo_id2'] != '01') & (edu2009bData['target_geo_id2'].notnull()) ]

edu2009bColsToRename =  {   'target_geo_id2'    : 'fips',
                            'percent'           : 'pct_bachelors'
                        }
edu2009bData = edu2009bData.rename(columns=edu2009bColsToRename)

edu2009bData = edu2009bData[['fips', 'pct_bachelors']]

edu09Data = pd.merge(edu2009hData, edu2009bData, how='left', on='fips')

# Load file into DataFrame
edu0017Data = openXlsFile(edu0017File, 'Education 1970 to 2017', 4)

# Fields to Rename
edu0017ColsToRename = { 'fips_code'                                                             : 'fips',
                    'less_than_a_high_school_diploma,1970'                                      : 'no_hs_diploma_1970',
                    'high_school_diploma_only,1970'                                             : 'hs_diploma_1970',
                    'some_college_(1_3_years),1970'                                             : 'some_college_1970',
                    'four_years_of_college_or_higher,1970'                                      : 'bach_plus_1970',
                    'percent_of_adults_with_less_than_a_high_school_diploma,1970'               : 'pct_no_hs_diploma_1970',
                    'percent_of_adults_with_a_high_school_diploma_only,1970'                    : 'pct_hs_diploma_1970',
                    'percent_of_adults_completing_some_college_(1_3_years),1970'                : 'pct_some_college_1970',
                    'percent_of_adults_completing_four_years_of_college_or_higher,1970'         : 'pct_bach_plus_1970',
                    'less_than_a_high_school_diploma,1980'                                      : 'no_hs_diploma_1980',
                    'high_school_diploma_only,1980'                                             : 'hs_diploma_1980',
                    'some_college_(1_3_years),1980'                                             : 'some_college_1980',
                    'four_years_of_college_or_higher,1980'                                      : 'bach_plus_1980',
                    'percent_of_adults_with_less_than_a_high_school_diploma,1980'               : 'pct_no_hs_diploma_1980',
                    'percent_of_adults_with_a_high_school_diploma_only,1980'                    : 'pct_hs_diploma_1980',
                    'percent_of_adults_completing_some_college_(1_3_years),1980'                : 'pct_some_college_1980',
                    'percent_of_adults_completing_four_years_of_college_or_higher,1980'         : 'pct_bach_plus_1980',
                    'less_than_a_high_school_diploma,1990'                                      : 'no_hs_diploma_1990',
                    'high_school_diploma_only,1990'                                             : 'hs_diploma_1990',
                    'some_college_or_associates_degree,1990'                                    : 'some_college_1990',
                    'bachelors_degree_or_higher,1990'                                           : 'bach_plus_1990',
                    'percent_of_adults_with_less_than_a_high_school_diploma,1990'               : 'pct_no_hs_diploma_1990',
                    'percent_of_adults_with_a_high_school_diploma_only,1990'                    : 'pct_hs_diploma_1990',
                    'percent_of_adults_completing_some_college_or_associates_degree,1990'       : 'pct_some_college_1990',
                    'percent_of_adults_with_a_bachelors_degree_or_higher,1990'                  : 'pct_bach_plus_1990',
                    'less_than_a_high_school_diploma,2000'                                      : 'no_hs_diploma_2000',
                    'high_school_diploma_only,2000'                                             : 'hs_diploma_2000',
                    'some_college_or_associates_degree,2000'                                    : 'some_college_2000',
                    'bachelors_degree_or_higher,2000'                                           : 'bach_plus_2000',
                    'percent_of_adults_with_less_than_a_high_school_diploma,2000'               : 'pct_no_hs_diploma_2000',
                    'percent_of_adults_with_a_high_school_diploma_only,2000'                    : 'pct_hs_diploma_2000',
                    'percent_of_adults_completing_some_college_or_associates_degree,2000'       : 'pct_some_college_2000',
                    'percent_of_adults_with_a_bachelors_degree_or_higher,2000'                  : 'pct_bachelors_2000',
                    'less_than_a_high_school_diploma,2013_17'                                   : 'no_hs_diploma_2013_2017',
                    'high_school_diploma_only,2013_17'                                          : 'hs_diploma_2013_2017',
                    'some_college_or_associates_degree,2013_17'                                 : 'some_college_2013_2017',
                    'bachelors_degree_or_higher,2013_17'                                        : 'bach_plus_2013_2017',
                    'percent_of_adults_with_less_than_a_high_school_diploma,2013_17'            : 'pct_no_hs_diploma_2013_2017',
                    'percent_of_adults_with_a_high_school_diploma_only,2013_17'                 : 'pct_hs_diploma_2017',
                    'percent_of_adults_completing_some_college_or_associates_degree,2013_17'    : 'pct_some_college_2013_2017',
                    'percent_of_adults_with_a_bachelors_degree_or_higher,2013_17'               : 'pct_bachelors_2017'
                  }

# Rename Fields
edu0017Data = edu0017Data.rename(columns=edu0017ColsToRename)

# List fields we want to keep
edu00ColsToKeep = [ 'fips',
                    'pct_hs_diploma_2000',                  # % HS Diploma Only
                    'pct_bachelors_2000'                    # % Bachelors degree or higher
                ]

edu17ColsToKeep = [ 'fips',
                    'pct_hs_diploma_2017',                  # % HS Diploma Only
                    'pct_bachelors_2017'                    # % Bachelors degree or higher
                ]
# Grab the columns we want
edu00Data = edu0017Data[edu00ColsToKeep]
edu17Data = edu0017Data[edu17ColsToKeep]

# Rename the fields
edu00Data = edu00Data.rename(columns={'pct_hs_diploma_2000' : 'pct_hs_diploma', 'pct_bachelors_2000' : 'pct_bachelors'})
edu17Data = edu17Data.rename(columns={'pct_hs_diploma_2017' : 'pct_hs_diploma', 'pct_bachelors_2017' : 'pct_bachelors'})

# Add representative year
edu00Data['year'] = '2000'
edu17Data['year'] = '2017'

# Reorder the fields
edu00Data = edu00Data[['fips','year','pct_hs_diploma','pct_bachelors']]
edu17Data = edu17Data[['fips','year','pct_hs_diploma','pct_bachelors']]

# Combine 2000, 2009, 2017
eduData = pd.concat([edu00Data, edu09Data, edu17Data])

if debug: 
    print()
    print("Education File:\n")
    print(eduData.head())
    print()

del edu0017Data
del edu00Data
del edu09Data
del edu17Data
del edu2009hData
del edu2009bData

# --------------------------------------------------------------------------------
## Process Poverty data

# Load files into DataFrames
pov00Data = openCsvFile(pov00File)
pov09Data = openCsvFile(pov09File)
pov17Data = openCsvFile(pov17File)

# Skip First line - 2000
pov00Headers    = pov00Data.iloc[0]
pov00Data       = pd.DataFrame(pov00Data.values[1:], columns=pov00Headers)
pov00Data       = stripWhiteSpace(pov00Data)
pov00Data       = pov00Data[(pov00Data['target_geo_id2'] != '01') & (pov00Data['target_geo_id2'].notnull()) ]
pov00Data['year'] = '2000'

# Skip First line - 2009
pov09Headers    = pov09Data.iloc[0]
pov09Data       = pd.DataFrame(pov09Data.values[1:], columns=pov09Headers)
pov09Data       = stripWhiteSpace(pov09Data)
pov09Data       = pov09Data[(pov09Data['target_geo_id2'] != '01') & (pov09Data['target_geo_id2'].notnull()) ]
pov09Data['year'] = '2010'

# Skip First line - 2017
pov17Headers    = pov17Data.iloc[0]
pov17Data       = pd.DataFrame(pov17Data.values[1:], columns=pov17Headers)
pov17Data       = stripWhiteSpace(pov17Data)
pov17Data       = pov17Data[(pov17Data['target_geo_id2'] != '01') & (pov17Data['target_geo_id2'].notnull()) ]
pov17Data['year'] = '2017'

# Fields to Rename
pov00ColsToRename = {   
    'target_geo_id2'                                                                                                : 'fips',
    'income_in_1999_below_poverty_level___percent_of_population_for_whom_poverty_status_is_determined___all_ages'   : 'pov_pct',
    'median_income_in_1999_(dollars)___households'                                                                  : 'median_hh_inc'
    }

pov09ColsToRename = {   
    'target_geo_id2'    : 'fips',
    'percent'           : 'pov_pct'    
    }

pov17ColsToRename = {   
    'target_geo_id2'    : 'fips',
    'percent'           : 'pov_pct'    
    }

# Rename Fields
pov00Data = pov00Data.rename(columns=pov00ColsToRename)
pov09Data = pov09Data.rename(columns=pov09ColsToRename)
pov17Data = pov17Data.rename(columns=pov17ColsToRename)

# Bring in Median Household Income
medHH09Data = openCsvFile(medHH09File)
medHH17Data = openCsvFile(medHH17File)

# Remove First Row
medHH09Headers    = medHH09Data.iloc[0]
medHH09Data       = pd.DataFrame(medHH09Data.values[1:], columns=medHH09Headers)
medHH09Data       = stripWhiteSpace(medHH09Data)

medHH17Headers    = medHH17Data.iloc[0]
medHH17Data       = pd.DataFrame(medHH17Data.values[1:], columns=medHH17Headers)
medHH17Data       = stripWhiteSpace(medHH17Data)

medHH09ColsToRename = {   
    'target_geo_id2'    : 'fips',
    'median'            : 'median_hh_inc'    
    }

medHH17ColsToRename = {   
    'target_geo_id2'    : 'fips',
    'dollar'            : 'median_hh_inc'    
    }

# Rename Fields
medHH09Data = medHH09Data.rename(columns=medHH09ColsToRename)
medHH17Data = medHH17Data.rename(columns=medHH17ColsToRename)

# Join Median Income onto poverty data
pov09Data = pd.merge(pov09Data, medHH09Data, how='left', on='fips')
pov17Data = pd.merge(pov17Data, medHH17Data, how='left', on='fips')

# List fields we want to keep
povColsToKeep = [   'fips',
                    'year',
                    'pov_pct',
                    'median_hh_inc'
                ]

# Grab the columns we want
pov00Data = pov00Data[povColsToKeep]
pov09Data = pov09Data[povColsToKeep]
pov17Data = pov17Data[povColsToKeep]

povData = pd.concat([pov00Data, pov09Data, pov17Data])

if debug: 
    print()
    print("Poverty File:\n")
    print(povData.head())
    print()

del pov00Data
del pov09Data
del pov17Data

# --------------------------------------------------------------------------------
## Process Unemployment data

# Load file into DataFrame
labor00Data = openXlsFile(labor00File,'laucnty00',5)
labor09Data = openXlsFile(labor09File,'laucnty09',5)
labor17Data = openXlsFile(labor17File,'laucnty17',5)

# labor Header
laborHeader = [ 'laus_code',
                'st_fips',
                'cty_fips',
                'area_name',
                'year',
                'blank',
                'labor_force',
                'employed',
                'unemployed',
                'unemploy_rate'
            ]

# Add the header
labor00Data.columns = laborHeader
labor09Data.columns = laborHeader
labor17Data.columns = laborHeader

# Set the representative year to 2010
labor09Data['year'] = '2010'

# Create full fips field
labor00Data['fips'] = labor00Data['st_fips'] + labor00Data['cty_fips']
labor09Data['fips'] = labor09Data['st_fips'] + labor09Data['cty_fips']
labor17Data['fips'] = labor17Data['st_fips'] + labor17Data['cty_fips']

# List fields we want to keep
laborColsToKeep = [ 'fips',
                    'year',
                    'unemploy_rate'
                ]
laborData = pd.concat([labor00Data, labor09Data, labor17Data])

laborData = laborData[laborColsToKeep]

if debug: 
    print()
    print("Unemployment File:\n")
    print(laborData.head())
    print()

# --------------------------------------------------------------------------------
## Process Demographic 2000-2003 Data

# Load 2010/2018 file into DataFrame
demo0003Data_a = openCsvFile(demo0003aFile)
demo0003Data_b = openCsvFile(demo0003bFile)

# Drop unneeded columns
demo0003Data_a = demo0003Data_a[['stcty','age','sex','race','origin','popestimate2000']]
demo0003Data_a = demo0003Data_a.rename(columns={'stcty' : 'fips',})
demo0003Data_b = demo0003Data_b[['stcty','age','sex','race','origin','popestimate2000']]
demo0003Data_b = demo0003Data_b.rename(columns={'stcty' : 'fips'})

# Get main population rows
demo0003Main_a = demo0003Data_a[(demo0003Data_a['age'] == '0') & (demo0003Data_a['sex'] == '0') & (demo0003Data_a['race'] == '0') & (demo0003Data_a['origin'] == '0') ]
demo0003Main_b = demo0003Data_b[(demo0003Data_b['age'] == '0') & (demo0003Data_b['sex'] == '0') & (demo0003Data_b['race'] == '0') & (demo0003Data_b['origin'] == '0') ]

demo0003Main = pd.concat([demo0003Main_a,demo0003Main_b])
demo0003Main['year'] = '2000'
demo0003Main = demo0003Main[['fips','year','popestimate2000']]
demo0003Main = demo0003Main.rename(columns={'popestimate2000' : 'population'})

del demo0003Main_a
del demo0003Main_b

# Sex : File A
demo0003Sex_a = demo0003Data_a[(demo0003Data_a['age'] == '0') & (demo0003Data_a['race'] == '0') & (demo0003Data_a['origin'] == '0')]
demo0003Sex_a = demo0003Sex_a[['fips','sex','popestimate2000']]

demo0003Sex_a_1 = demo0003Sex_a[(demo0003Sex_a['sex'] == "1")]
demo0003Sex_a_1 = demo0003Sex_a_1.rename(columns={'popestimate2000' : 'tot_male'})
demo0003Sex_a_1 = demo0003Sex_a_1[['fips','tot_male']]

demo0003Sex_a_2 = demo0003Sex_a[(demo0003Sex_a['sex'] == "2")] 
demo0003Sex_a_2 = demo0003Sex_a_2.rename(columns={'popestimate2000' : 'tot_female'})
demo0003Sex_a_2 = demo0003Sex_a_2[['fips','tot_female']]

# Sex : File B
demo0003Sex_b = demo0003Data_b[(demo0003Data_b['age'] == '0') & (demo0003Data_b['race'] == '0') & (demo0003Data_b['origin'] == '0')]
demo0003Sex_b = demo0003Sex_b[['fips','sex','popestimate2000']]
demo0003Sex_b_1 = demo0003Sex_b[(demo0003Sex_b['sex'] == "1")]
demo0003Sex_b_1 = demo0003Sex_b_1.rename(columns={'popestimate2000' : 'tot_male'})
demo0003Sex_b_1 = demo0003Sex_b_1[['fips','tot_male']]

demo0003Sex_b_2 = demo0003Sex_b[(demo0003Sex_b['sex'] == "2")] 
demo0003Sex_b_2 = demo0003Sex_b_2.rename(columns={'popestimate2000' : 'tot_female'})
demo0003Sex_b_2 = demo0003Sex_b_2[['fips','tot_female']]

# Sex Combined
demo0003Sex_male = pd.concat([demo0003Sex_a_1, demo0003Sex_b_1])
demo0003Sex_female = pd.concat([demo0003Sex_a_2, demo0003Sex_b_2])

del demo0003Sex_a
del demo0003Sex_b
del demo0003Sex_a_1
del demo0003Sex_a_2
del demo0003Sex_b_1
del demo0003Sex_b_2

# Age : File A
demo0003Age_a = demo0003Data_a[(demo0003Data_a['sex'] == '0') & (demo0003Data_a['race'] == '0') & (demo0003Data_a['origin'] == '0')]
demo0003Age_a = demo0003Age_a[['fips','age','popestimate2000']]
demo0003Age_a = demo0003Age_a[(demo0003Age_a['age'] == "4") | (demo0003Age_a['age'] == "5") | (demo0003Age_a['age'] == "6") | (demo0003Age_a['age'] == "7") | (demo0003Age_a['age'] == "8")]
demo0003Age_a['age'] = "age_grp_" + demo0003Age_a['age']
demo0003Age_aPivot = demo0003Age_a.pivot(index='fips', columns='age', values='popestimate2000').reset_index()

# Age : File B
demo0003Age_b = demo0003Data_b[(demo0003Data_b['sex'] == '0') & (demo0003Data_b['race'] == '0') & (demo0003Data_b['origin'] == '0')]
demo0003Age_b = demo0003Age_b[['fips','age','popestimate2000']]
demo0003Age_b = demo0003Age_b[(demo0003Age_b['age'] == "4") | (demo0003Age_b['age'] == "5") | (demo0003Age_b['age'] == "6") | (demo0003Age_b['age'] == "7") | (demo0003Age_b['age'] == "8")]
demo0003Age_b['age'] = "age_grp_" + demo0003Age_b['age']
demo0003Age_bPivot = demo0003Age_b.pivot(index='fips', columns='age', values='popestimate2000').reset_index()

# Age Combined
demo0003Age = pd.concat([demo0003Age_aPivot,demo0003Age_bPivot])

del demo0003Age_a
del demo0003Age_aPivot
del demo0003Age_b
del demo0003Age_bPivot

# Race : File A
demo0003Race_a = demo0003Data_a[(demo0003Data_a['age'] == '0') & (demo0003Data_a['sex'] == '0') & (demo0003Data_a['origin'] == '0')]
demo0003Race_a = demo0003Race_a[['fips','race','popestimate2000']]
demo0003Race_a = demo0003Race_a[(demo0003Race_a['race'] == '1') | (demo0003Race_a['race'] == '2') | (demo0003Race_a['race'] == '3') | (demo0003Race_a['race'] == '4')]

# Map Race IDs to consistent codes
race_a_conditions = [
    demo0003Race_a['race'] == '1',
    demo0003Race_a['race'] == '2',
    demo0003Race_a['race'] == '3',
    demo0003Race_a['race'] == '4'
]

race_maps = ['wa','ba','ia','aa']

demo0003Race_a['race'] = np.select(race_a_conditions, race_maps, default = "")

# Grab hispanic count
demo0003Race_a_h = demo0003Data_a[(demo0003Data_a['age'] == '0') & (demo0003Data_a['sex'] == '0') & (demo0003Data_a['race'] == '0') & (demo0003Data_a['origin'] == '2')]
demo0003Race_a_h = demo0003Race_a_h[['fips','race','popestimate2000']]
demo0003Race_a_h['race'] = 'h'

# Merge and Pivot
demo0003Race_a = pd.concat([demo0003Race_a,demo0003Race_a_h])
demo0003Race_aPivot = demo0003Race_a.pivot(index='fips', columns='race', values='popestimate2000').reset_index()
demo0003Race_aPivot = demo0003Race_aPivot[['fips','wa','ba','ia','aa','h']]

# Race : File B
demo0003Race_b = demo0003Data_b[(demo0003Data_b['age'] == '0') & (demo0003Data_b['sex'] == '0') & (demo0003Data_b['origin'] == '0')]
demo0003Race_b = demo0003Race_b[['fips','race','popestimate2000']]
demo0003Race_b = demo0003Race_b[(demo0003Race_b['race'] == '1') | (demo0003Race_b['race'] == '2') | (demo0003Race_b['race'] == '3') | (demo0003Race_b['race'] == '4')]

# Map Race IDs to consistent codes
race_b_conditions = [
    demo0003Race_b['race'] == '1',
    demo0003Race_b['race'] == '2',
    demo0003Race_b['race'] == '3',
    demo0003Race_b['race'] == '4'
]

demo0003Race_b['race'] = np.select(race_b_conditions, race_maps, default = "")

# Grab hispanic count
demo0003Race_b_h = demo0003Data_b[(demo0003Data_b['age'] == '0') & (demo0003Data_b['sex'] == '0') & (demo0003Data_b['race'] == '0') & (demo0003Data_b['origin'] == '2')]
demo0003Race_b_h = demo0003Race_b_h[['fips','race','popestimate2000']]
demo0003Race_b_h['race'] = 'h'

# Merge and Pivot
demo0003Race_b = pd.concat([demo0003Race_b,demo0003Race_b_h])
demo0003Race_bPivot = demo0003Race_b.pivot(index='fips', columns='race', values='popestimate2000').reset_index()
demo0003Race_bPivot = demo0003Race_bPivot[['fips','wa','ba','ia','aa','h']]

# Combine the two files
demo0003Race = pd.concat([demo0003Race_aPivot, demo0003Race_bPivot])

del demo0003Race_a
del demo0003Race_aPivot
del demo0003Race_b
del demo0003Race_bPivot

# Join all the demographic data together
demo0003Main = pd.merge(demo0003Main, demo0003Sex_male, how='left', on='fips')
demo0003Main = pd.merge(demo0003Main, demo0003Sex_female, how='left', on='fips')
demo0003Main = pd.merge(demo0003Main, demo0003Race, how='left', on='fips')
demo0003Main = pd.merge(demo0003Main, demo0003Age, how='left', on='fips')

del demo0003Data_a
del demo0003Data_b
del demo0003Sex_male
del demo0003Sex_female
del demo0003Age
del demo0003Race

# --------------------------------------------------------------------------------
## Process Demographic 2010-2018 Data

# Load 2010/2018 file into DataFrame
demo1018Data = openCsvFile(demo1018File)
demo1018Data = demo1018Data.rename(columns={'tot_pop' : 'population'})

# Filter for just the years we want (2010=3 and 2017=10)
demo1018Data = demo1018Data[(demo1018Data['year'] == "3") | (demo1018Data['year'] == '10') ]

# Generate the fips code
demo1018Data['fips'] = demo1018Data['state'] + demo1018Data['county']

# Get the population total record (all ages)
demo1018Main = demo1018Data[demo1018Data['agegrp'] == "0"]

# Get the Various Age Group Population Totals and Pivot for 2010
demo10AgeTotals = demo1018Data[ (demo1018Data['agegrp'] != "0") & (demo1018Data['year'] == "3")]
demo10AgeTotals = demo10AgeTotals[['fips', 'agegrp','population']]
demo10AgeTotals['agegrp'] = "age_grp_" + demo10AgeTotals['agegrp']
demo10AgePivot = demo10AgeTotals.pivot(index='fips', columns='agegrp', values='population').reset_index()
demo10AgePivot['year'] = "3"
demo10AgePivot = demo10AgePivot[['fips','year','age_grp_4','age_grp_5','age_grp_6','age_grp_7','age_grp_8']]

#print(demo10AgePivot.head())

# Get the Various Age Group Population Totals and Pivot for 2017
demo17AgeTotals = demo1018Data[ (demo1018Data['agegrp'] != "0") & (demo1018Data['year'] == "10")]
demo17AgeTotals = demo17AgeTotals[['fips', 'agegrp','population']]
demo17AgeTotals['agegrp'] = "age_grp_" + demo17AgeTotals['agegrp']
demo17AgePivot = demo17AgeTotals.pivot(index='fips', columns='agegrp', values='population').reset_index()
demo17AgePivot['year'] = "10"
demo17AgePivot = demo17AgePivot[['fips','year','age_grp_4','age_grp_5','age_grp_6','age_grp_7','age_grp_8']]

demo1018AgePivot = pd.concat([demo10AgePivot,demo17AgePivot])

# Join the Age Group Totals onto the main population total records
demo1018Main = pd.merge(demo1018Main,demo1018AgePivot, how="left", on=["fips","year"])

# Combine ethnic gender buckets to have one count per ethnicity
demo1018Main['wa'] = pd.to_numeric(demo1018Main['wa_male']) + pd.to_numeric(demo1018Main['wa_female'])
demo1018Main['ba'] = pd.to_numeric(demo1018Main['ba_male']) + pd.to_numeric(demo1018Main['ba_female'])
demo1018Main['ia'] = pd.to_numeric(demo1018Main['ia_male']) + pd.to_numeric(demo1018Main['ia_female'])
demo1018Main['aa'] = pd.to_numeric(demo1018Main['aa_male']) + pd.to_numeric(demo1018Main['aa_female'])
demo1018Main['h']  = pd.to_numeric(demo1018Main['h_male'])  + pd.to_numeric(demo1018Main['h_female'])

# Columns to keep
demo1018ColsToKeep = [
                        'fips',
                        'year',
                        'population',                   # Total population
                        'tot_male',                     # Total Male population
                        'tot_female',                   # Total Female population
                        'wa',                           # White-alone population
                        'ba',                           # Black or African American alone population
                        'ia',                           # American Indian and Alaska Native alone population
                        'aa',                           # Asian alone population
                        'h',                            # Hispanic population
                        'age_grp_4',                    # Total Population in Age Group 4 (15-19 yrs)
                        'age_grp_5',                    # Total Population in Age Group 5 (20-24 yrs)
                        'age_grp_6',                    # Total Population in Age Group 6 (25-29 yrs)
                        'age_grp_7',                    # Total Population in Age Group 7 (30-34 yrs)
                        'age_grp_8'                     # Total Population in Age Group 8 (35-39 yrs)
                    ]


# Fields removed:
'''
                        'tot_pop',                      # Total population
                        'wa_male',                      # White-alone Male population
                        'wa_female',                    # White-alone Female population
                        'ba_male',                      # Black or African American alone male population
                        'ba_female',                    # Black or African American alone female population
                        'ia_male',                      # American Indian and Alaska Native alone male population
                        'ia_female',                    # American Indian and Alaska Native alone female population
                        'aa_male',                      # Asian alone male population
                        'aa_female',                    # Asian alone female population
                        'h_male',                       # Hispanic male population
                        'h_female',                     # Hispanic female population
'''

# Update year from codes to years
demo1018Main['year'] = np.where(demo1018Main['year'] == '3','2010','2017')

# Grab the columns we want
demo1018Main = demo1018Main[demo1018ColsToKeep]

del demo1018Data
del demo1018AgePivot

# Combine all Demographic Data (2000,2010,2017)
demoData = pd.concat([demo0003Main, demo1018Main])

del demo0003Main
del demo1018Main

if debug: 
    print()
    print("Demo Data:\n")
    print(demoData.head())
    print()

# --------------------------------------------------------------------------------
## Create Data Input to Prediction

# Join on all the ancillary data to the CDC Wonder data
predInput = pd.merge(cdcData,   eduData,    how="left", on=["fips","year"])
predInput = pd.merge(predInput, laborData,  how="left", on=["fips","year"])
predInput = pd.merge(predInput, demoData,   how="left", on=["fips","year"])
predInput = pd.merge(predInput, povData,    how="left", on=["fips","year"])

# Impute death numbers of Suppressed records based on county population
predInputSuppressed = predInput[predInput['deaths'] == 'Suppressed'].copy()

predInputSuppressed['scaled_pop'] = predInputSuppressed['population']
predInputSuppressed['scaled_pop'].fillna(0, inplace=True)
#predInputSuppressed['scaled_pop'] = pd.to_numeric(predInputSuppressed['scaled_pop'], errors='coerce')
predInputSuppressed['scaled_pop'] = predInputSuppressed['scaled_pop'].astype(float)

predInputSuppressed['scaled_pop'] -= predInputSuppressed['scaled_pop'].min()
predInputSuppressed['scaled_pop'] /= predInputSuppressed['scaled_pop'].max()

predInputSuppressed['scaled_pop'] = np.floor(predInputSuppressed['scaled_pop'] * 9)

predInputSuppressed = predInputSuppressed[['fips','year','scaled_pop']]

predInput = pd.merge(predInput, predInputSuppressed,    how="left", on=["fips","year"])

# Scale response to between 0 and 9 if it's suppressed
predInput.loc[predInput.deaths          == 'Suppressed', 'deaths'] = predInput['scaled_pop']
predInput.loc[predInput.deaths_age_adj  == 'Suppressed', 'deaths_age_adj'] = predInput['scaled_pop']

writeTabFile(predInput, predInputOut)



# Reorder the columns
predInputCols = [       'fips',
                        'county',
                        'population',
                        'tot_male',
                        'tot_female',
                        'wa',
                        'ba',
                        'ia',
                        'aa',
                        'h',
                        'age_grp_4',
                        'age_grp_5',
                        'age_grp_6',
                        'age_grp_7',
                        'age_grp_8',
                        'year',
                        'year_min',
                        'year_max',
                        'pct_hs_diploma',
                        'pct_bachelors',
                        'pov_pct',
                        'median_hh_inc',
                        'unemploy_rate',
                        'deaths',
                        'deaths_age_adj'
                    ]

predInput = predInput[predInputCols]

predInput = predInput.sort_values(['fips','year'])

# Write to tab file
writeTabFile(predInput, predInputOut)

if debug: 
    print()
    print("Prediction Input File:\n")
    print(predInput.head())
    print()


# --------------------------------------------------------------------------------
## Process Lat/Lon Data

# Load file into DataFrame
countyData = openTabFile(countyFile)

# Add text label field for mouseover hover
countyData['label'] = countyData['name'] + ", " + countyData['usps']

if debug: 
    print()
    print("County Lat/Lon File:\n")
    print(countyData.head())
    print()

# Write cleaned-up file
writeTabFile(countyData, countyOut)

# --------------------------------------------------------------------------------
## State Data

# State Populations
statePopData = openCsvFile(statePopFile)
statePopData['fips'] = statePopData['fips'] + "000"

statePopColsToRename = {
    'state_population_2000' : 'population_2000',
    'state_population_2010' : 'population_2010',
    'state_population_2017' : 'population_2017'
}
statePopData = statePopData.rename(columns=statePopColsToRename)
statePopData = statePopData[['fips','population_2000','population_2010','population_2017']]

# State CDC Data
state00Data = openTabFile(cdcState00File)
state10Data = openTabFile(cdcState10File)
state17Data = openTabFile(cdcState17File)

state00Data['year'] = "2000"
state10Data['year'] = "2010"
state17Data['year'] = "2017"

stateData = pd.concat([state00Data, state10Data, state17Data])
stateData = stateData[pd.isnull(stateData['notes'])]

stateData['fips'] = stateData['state_code'] + "000"
stateData["county"] = ""

stateData['mean_deaths'] = pd.to_numeric(stateData['deaths'], errors='coerce') / 6

stateData = stateData.rename(columns={'age_adjusted_rate' : 'deaths_age_adj'})

stateNumCols = [
    'fips',
    'year',
    'deaths',
    'mean_deaths',
    'deaths_age_adj'
]

stateDataNums = stateData[stateNumCols]

stateDataNums = stateDataNums.pivot(index='fips', columns='year', values=['deaths', 'mean_deaths', 'deaths_age_adj']).reset_index()
stateDataNums.columns = stateDataNums.columns.to_series().str.join('_')
stateDataNums = stateDataNums.rename(columns={'fips_':'fips'})

stateDataDemo = stateData[['fips','county','state']]
stateDataDemo = stateDataDemo.drop_duplicates()

stateData = pd.merge(stateDataNums, stateDataDemo,  how='left', on='fips')
stateData = pd.merge(stateData, statePopData,   how='left', on='fips')

stateData['md_per_100k_2000'] = stateData['mean_deaths_2000'] / (pd.to_numeric(stateData['population_2000'], errors='coerce') / 100000 )
stateData['md_per_100k_2010'] = stateData['mean_deaths_2010'] / (pd.to_numeric(stateData['population_2010'], errors='coerce') / 100000 )
stateData['md_per_100k_2017'] = stateData['mean_deaths_2017'] / (pd.to_numeric(stateData['population_2017'], errors='coerce') / 100000 )

stateData['label'] = stateData['state']

stateDataCols = [
    'fips',
    'population_2000',
    'population_2010',
    'population_2017',
    'deaths_2000',
    'deaths_2010',
    'deaths_2017',
    'md_per_100k_2000',
    'md_per_100k_2010',
    'md_per_100k_2017',
    'deaths_age_adj_2000',
    'deaths_age_adj_2010',
    'deaths_age_adj_2017',
    'county',
    'state',
    'label'
]

stateData = stateData[stateDataCols]

if debug: 
    print()
    print("State File:\n")
    print(stateData.head())
    print()


# --------------------------------------------------------------------------------
## Create Choropleth Input Data - Investigation section

# Start with pred input
mapData = predInput.copy()

# Calculate mean deaths per 100k population
mapData['mean_deaths'] = pd.to_numeric(mapData['deaths'], errors='coerce') / 6
mapData['md_per_100k'] = mapData['mean_deaths'] / (pd.to_numeric(mapData['population'], errors='coerce') / 100000 )

# Grab the fields we want and write the output file
mapData = mapData[['fips','year','population','deaths','md_per_100k', 'deaths_age_adj']]

# Pivot counts / denormalize
mapData = mapData.pivot(index='fips', columns='year', values=['population','deaths','md_per_100k', 'deaths_age_adj']).reset_index()
mapData.columns = mapData.columns.to_series().str.join('_')
mapData = mapData.rename(columns={'fips_':'fips'})

# Join on the county, state, and mouseover label
countyLabels = countyData[["geoid","name","usps","label"]]
countyLabels = countyLabels.rename(columns={'geoid':'fips', 'name': 'county','usps':'state'})
mapData = pd.merge(mapData, countyLabels, how="inner", on="fips")

# Merge in the state data
mapData = pd.concat([mapData, stateData])


if debug: 
    print()
    print("Map Input File:\n")
    print(mapData.head())
    print()

writeTabFile(mapData, mapOut)

# --------------------------------------------------------------------------------
## Create subplot input file

# Start with pred input
subInput = predInput.copy()

subPivotCols = [
    'population',
    'tot_male',
    'tot_female',
    'wa',
    'ba',
    'ia',
    'aa',
    'h',
    'age_grp_4',
    'age_grp_5',
    'age_grp_6',
    'age_grp_7',
    'age_grp_8',
    'pct_hs_diploma',
    'pct_bachelors',
    'pov_pct',
    'median_hh_inc',
    'unemploy_rate',
    'deaths',
    'deaths_age_adj'
]

subInput = subInput.pivot(index='fips', columns='year', values=subPivotCols).reset_index()
subInput.columns = subInput.columns.to_series().str.join('_')
subInput = subInput.rename(columns={'fips_':'fips'})

mdpo = mapData.copy()
mdpo = mdpo[['fips','md_per_100k_2000','md_per_100k_2010','md_per_100k_2017']]

subInput = pd.merge(subInput, mdpo,    how="left", on="fips")


if debug: 
    print()
    print("Investige Sub Plot Input File:\n")
    print(subInput.head())
    print()

writeTabFile(subInput, subOut)

del subInput

# --------------------------------------------------------------------------------
## Create Choropleth Input Data - Prediction section

predictMapData = mapData.copy()
del mapData

# Read in the prediction data
deathRateData = openCsvFile(deathRateFile)
deathAdjData  = openCsvFile(deathAdjFile)

deathRateData = deathRateData[['fips','predicted_death_rate']]
deathRateData = deathRateData.rename(columns={'predicted_death_rate':'md_per_100k_2024'})

deathAdjData = deathAdjData[['fips','predicted_deaths_age_adj']]
deathAdjData = deathAdjData.rename(columns={'predicted_deaths_age_adj':'deaths_age_adj_2024'})

predictMapData = pd.merge(predictMapData, deathRateData, how="left", on="fips")
predictMapData = pd.merge(predictMapData, deathAdjData,  how="left", on="fips")

# Grab state records and remove the data fields
predictMapStateRows = predictMapData[predictMapData['fips'].str.endswith("000")].copy()

predictMapStateRows.drop(['md_per_100k_2024','deaths_age_adj_2024'], axis=1, inplace=True)


# Grab county records and average at the state-level
predictMapCtyRows = predictMapData[~predictMapData['fips'].str.endswith("000")]

predictMapCtyRowsCopy = predictMapCtyRows.copy()
predictMapCtyRowsCopy['md_per_100k_2024']       = predictMapCtyRowsCopy['md_per_100k_2024'].astype(float)
predictMapCtyRowsCopy['deaths_age_adj_2024']    = predictMapCtyRowsCopy['deaths_age_adj_2024'].astype(float)
predictMapCtyMD =       predictMapCtyRowsCopy.groupby(['state'])['md_per_100k_2024'].mean().reset_index()
predictMapCtyAgeAdj =   predictMapCtyRowsCopy.groupby(['state'])['deaths_age_adj_2024'].mean().reset_index()


stateLabels = {
    'Alabama':'AL',
    'Alaska':'AK',
    'Arizona':'AZ',
    'Arkansas':'AR',
    'California':'CA',
    'Colorado':'CO',
    'Connecticut':'CT',
    'Delaware':'DE',
    'Florida':'FL',
    'Georgia':'GA',
    'Hawaii':'HI',
    'Idaho':'ID',
    'Illinois':'IL',
    'Indiana':'IN',
    'Iowa':'IA',
    'Kansas':'KS',
    'Kentucky':'KY',
    'Louisiana':'LA',
    'Maine':'ME',
    'Maryland':'MD',
    'Massachusetts':'MA',
    'Michigan':'MI',
    'Minnesota':'MN',
    'Mississippi':'MS',
    'Missouri':'MO',
    'Montana':'MT',
    'Nebraska':'NE',
    'Nevada':'NV',
    'New Hampshire':'NH',
    'New Jersey':'NJ',
    'New Mexico':'NM',
    'New York':'NY',
    'North Carolina':'NC',
    'North Dakota':'ND',
    'Ohio':'OH',
    'Oklahoma':'OK',
    'Oregon':'OR',
    'Pennsylvania':'PA',
    'Rhode Island':'RI',
    'South Carolina':'SC',
    'South Dakota':'SD',
    'Tennessee':'TN',
    'Texas':'TX',
    'Utah':'UT',
    'Vermont':'VT',
    'Virginia':'VA',
    'Washington':'WA',
    'West Virginia':'WV',
    'Wisconsin':'WI',
    'Wyoming':'WY',
    'District of Columbia':'DC',
    'Marshall Islands':'MH',
    'Armed Forces Africa':'AE',
    'Armed Forces Americas':'AA',
    'Armed Forces Canada':'AE',
    'Armed Forces Europe':'AE',
    'Armed Forces Middle East':'AE',
    'Armed Forces Pacific':'AP'
}

predictMapStateRows['state'].replace(stateLabels, inplace=True)


# Join County Means onto the state records
predictMapStateRows = pd.merge(predictMapStateRows, predictMapCtyMD, how="left", on="state")
predictMapStateRows = pd.merge(predictMapStateRows, predictMapCtyAgeAdj, how="left", on="state")

# Combine state + county records
predictMapData = pd.concat([predictMapCtyRows,predictMapStateRows])

if debug: 
    print()
    print("Map Input File - Prediction:\n")
    print(predictMapData.head())
    print()

writeTabFile(predictMapData, predictMapOut)

