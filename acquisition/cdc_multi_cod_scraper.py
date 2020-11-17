
import requests
from selenium import webdriver
import re
import pandas as pd
import json
import csv
from csv import DictWriter
import os
import sys
import time
# --------------------------------------------------------------------------------
## Toggles

# Enable more logging
debug = True

# Additional Request Group-bys - By default it Groups by County
GROUPBY_UCD         = False         # Whether to group by UCD

# Request Filters: 
GEO_COUNTY          = False         # True to filter the request by county, False to filter the request by State (and group by County)
UCD_MCD_FILTER      = True          # Filter for UCD and MCD combinations
AGE_FILTER          = False         # Filter by Age Group (10-year)
SEX_FILTER          = False         # Filter by Gender
RACE_FILTER         = False         # Filter by Race
YEAR_FILTER         = True          # Filter by Year

# Request Toggles 
NO_REQUEST          = False         # If True: Stop before making any request - overrides all below settings
SINGLE_REQUEST      = False         # Single Request - if you only want to make one request (and not loop)
TESTING             = False         # If True: will use smaller input parameter files and limit # of iterations
REQUEST_SLEEP       = False         # If True: will sleep 1 second between requests
GROUP_YEARS         = 6             # False or N: If not False: groups N yrs as one request. Must use YEAR_FILTER = True

# --------------------------------------------------------------------------------
## Parameters

# URL For the page where you have to click "I Agree" button
agreeurl = "https://wonder.cdc.gov/mcd-icd10.html"

# Output Directory - where to write the data files
outDir = "cdc_mcd_data/"

# Request Log
requestLogFile = outDir + "request_log.txt"

# List of keys in parameter files to ignore (don't iterate with these)
keyBlacklist = "*All*"

if debug :
    print()
    print("----------------------------------")
    print("Initial URL:\t"+agreeurl)
    print("Output Dir:\t"+outDir)
    print("Request Log:\t"+requestLogFile)
    print()
    print("Toggles:")
    if NO_REQUEST :
        print("\tNo Request:\tTrue")
    else :
        print("\tNo Request:\tFalse")
    if SINGLE_REQUEST :
        print("\tSingle Request:\tTrue")
    else :
        print("\tSingle Request:\tFalse")
    if TESTING :
        print("\tTesting Mode:\tTrue")
    else :
        print("\tTesting Mode:\tFalse")
    if REQUEST_SLEEP :
        print("\tSleep Requests:\tTrue")
    else :
        print("\tSleep Requests:\tFalse")
    if GROUP_YEARS :
        print("\tGroup Years:\t"+str(GROUP_YEARS)+ " year increments")
    else :
        print("\tGroup Years:\tFalse")
    print()
    print("Group by:")
    if GEO_COUNTY :
        print("\tCounty:\t\tFalse")
    else :
        print("\tCounty:\t\tTrue")
    print("\tUCD:\t\t"+str(GROUPBY_UCD))
    print()
    print("Filters:")
    if GEO_COUNTY :
        print("\tGeography:\t\tCounty")
    else :
        print("\tGeography:\tState")
    print("\tUCD_MCD:\t"+str(UCD_MCD_FILTER))
    print("\tAge:\t\t"+str(AGE_FILTER))
    print("\tSex:\t\t"+str(SEX_FILTER))
    print("\tRace:\t\t"+str(RACE_FILTER))
    print("\tYear:\t\t"+str(YEAR_FILTER))
    print()

# --------------------------------------------------------------------------------
## Functions

def get_filename_from_cd(cd):
    """
    Get filename from content-disposition
    """
    if not cd:
        return None
    fname = re.findall('filename=(.+)', cd)
    if len(fname) == 0:
        return None
    return fname[0].replace('"','')

def csvParamReader(fn) :
    """
    Open a two-column csv file and return a dictionary
    """
    with open (fn, 'r') as f:
        reader = csv.reader(f)
        next(reader, None) # skip the header
        l =  list(reader)
        myDict = dict((row[0],row[1]) for row in l if row[0] not in keyBlacklist)

    return myDict

def chunkYears(y,n) :
    '''
    Take in a sorted array of years (y), chunk to n groups, and return
    '''
    for i in range(0, len(y), n) :
        yield y[i:i+n]

# --------------------------------------------------------------------------------
## Input Data / Config

# Location of parameter csv files
paramDir = "parameter_values/"

# List of Parameter Files
statesFile   = 'state_codes_V_D77.V9.csv'
countiesFile = 'counties_D77.V9.csv'
yearsFile    = "years_F_D77.V1.csv"
monthsFile   = "months.csv"
agesFile     = 'age_groups_D77.V5.csv'
racesFile    = 'races_D77.V8.csv'
sexesFile    = 'sexes_D77.V7.csv'

if TESTING : # Use smaller files
    statesFile   = 'small_' + statesFile
    countiesFile = 'small_' + countiesFile
    yearsFile    = 'small_' + yearsFile
    agesFile     = 'small_' + agesFile
    # no need for smaller races file
    # no need for smaller sexes file

# Read Parameters Files into dictionaries
if GEO_COUNTY :
    geos = csvParamReader(paramDir+countiesFile)
else :
    geos = csvParamReader(paramDir+statesFile)

#states   = csvParamReader(paramDir+statesFile)
#counties = csvParamReader(paramDir+countiesFile)

years = {"*All*":"All"}
ages =  {"*All*":"All"}
races = {"*All*":"All"}
sexes = {"*All*":"All"}

# If we want to filter on a specific parameter, load that data in for iteration
if YEAR_FILTER  : years    = csvParamReader(paramDir+yearsFile)
if AGE_FILTER   : ages     = csvParamReader(paramDir+agesFile)
if RACE_FILTER  : races    = csvParamReader(paramDir+racesFile)
if SEX_FILTER   : sexes    = csvParamReader(paramDir+sexesFile)

#months   = csvParamReader(paramDir+monthsFile)

if GROUP_YEARS :
    all_yrs = sorted(years, key=lambda key: years[key])
    years = list(chunkYears(all_yrs,GROUP_YEARS))
    
    if debug: 
        print("> Grouping Years in "+str(GROUP_YEARS)+" increments:")
        print("\t",years)
        print()

# Go state-by-state for now
#geos = {
#    '01' : 'Alabama'
    #'06' : 'California'
#}

#years = {
#    '2015' : '2015'
#}

# Create a lits of items to loop over (to avoid crazy nested loops)
iterKey = {
    "geo"    : 0,
    "year"   : 1,
    "sex"    : 2,
    "age"    : 3,
    "race"   : 4
}

if SINGLE_REQUEST : # If you just want to do a single request, manually set your parameters here

    if debug: print("> Issue Single Request")

    # Set your parameters
    #st = "02"
    #cty = "01015"
    geo = "06"
    yr = "2015"
    sex = "M"
    age = "5-14"
    race = "2106-3"

    iterations = [(geo,yr,sex,age,race)]

else : # Otherwise we'll iterate over the different parameters
    
    iterations = [(a,b,c,d,e)   for a in geos
                                for b in years 
                                for c in sexes 
                                for d in ages 
                                for e in races
    ]

#pprint(iterations)

# Create state-level output directories for data
for g in geos.keys() :
    if not os.path.exists(outDir+g):
        os.makedirs(outDir+g)
    
    # Delete result files already in that directory
    filelist = [ f for f in os.listdir(outDir+g) if f.endswith(".tab") ]
    for f in filelist:
        os.remove(os.path.join(outDir+g, f))

# --------------------------------------------------------------------------------
## Create the base request package

# Read in the template request file
requestFile = "requests/post_data.json"
requestData = json.load(open(requestFile))

if GEO_COUNTY : # If we want to request by county instead of state, we don't need to group by county
    
    if GROUPBY_UCD : # If we want to group by UCD, set B_1
        requestData['B_1'] =  "D77.V2-level3"

else : # Otherwise, we will request by state, so we want to group by county
    requestData['B_1'] = "D77.V9-level2" 

    if GROUPBY_UCD : # If we also want to group by UCD, set it to B_2
        requestData['B_2'] =  "D77.V2-level3"


if UCD_MCD_FILTER : # If we want to filter only for UCD / MCD deaths, this will set that

    # Set UCD Filter
    requestData['F_D77.V2'] = ['X40', 'X41', 'X42', 'X43', 'X44', 'X49', 'X60', 'X61', 'X62', 'X63', 'X64', 'X83', 'X84', 'X85', 'Y10', 'Y11', 'Y12', 'Y13', 'Y14', 'Y33', 'Y34']

    #requestData['I_D77.V2'] = "X40 (Accidental poisoning by and exposure to nonopioid analgesics, antipyretics and antirheumatics)X41 (Accidental poisoning by and exposure to antiepileptic, sedative-hypnotic, antiparkinsonism and psychotropic drugs, not elsewhere classified)X42 (Accidental poisoning by and exposure to narcotics and psychodysleptics [hallucinogens], not elsewhere classified)X43 (Accidental poisoning by and exposure to other drugs acting on the autonomic nervous system)X44 (Accidental poisoning by and exposure to other and unspecified drugs, medicaments and biological substances)X49 (Accidental poisoning by and exposure to other and unspecified chemicals and noxious substances)X60 (Intentional self-poisoning by and exposure to nonopioid analgesics, antipyretics and antirheumatics)X61 (Intentional self-poisoning by and exposure to antiepileptic, sedative-hypnotic, antiparkinsonism and psychotropic drugs, not elsewhere classified)X62 (Intentional self-poisoning by and exposure to narcotics and psychodysleptics [hallucinogens], not elsewhere classified)X63 (Intentional self-poisoning by and exposure to other drugs acting on the autonomic nervous system)X64 (Intentional self-poisoning by and exposure to other and unspecified drugs, medicaments and biological substances)X83 (Intentional self-harm by other specified means)X84 (Intentional self-harm by unspecified means)X85 (Assault by drugs, medicaments and biological substances)Y10 (Poisoning by and exposure to nonopioid analgesics, antipyretics and antirheumatics, undetermined intent)Y11 (Poisoning by and exposure to antiepileptic, sedative-hypnotic, antiparkinsonism and psychotropic drugs, not elsewhere classified, undetermined intent)Y12 (Poisoning by and exposure to narcotics and psychodysleptics [hallucinogens], not elsewhere classified, undetermined intent)Y13 (Poisoning by and exposure to other drugs acting on the autonomic nervous system, undetermined intent)Y14 (Poisoning by and exposure to other and unspecified drugs, medicaments and biological substances, undetermined intent)Y33 (Other specified events, undetermined intent)Y34 (Unspecified event, undetermined intent)"

    # Set MCD Filter
    requestData['F_D77.V13'] = ['T40.0', 'T40.1', 'T40.2', 'T40.3', 'T40.4', 'T40.6']
    requestData['V_D77.V13'] = "T40.0 (Opium)\r\nT40.1 (Heroin)\r\nT40.2 (Other opioids)\r\nT40.3 (Methadone)\r\nT40.4 (Other synthetic narcotics)\r\nT40.6 (Other and unspecified narcotics)\r\n"


# Print out the request package
#print(json.dumps(requestData, indent=4))

# Will exit before making any requests or launching the browser
if NO_REQUEST : 
    sys.exit()

# --------------------------------------------------------------------------------
## Get the Session ID and cookies with Selenium

if debug: print("> Launching Chrome")
# Uses Selenium to launch Chrome, go to the agreeurl and click the "I Agree" button
# This uses Chrome 77 (driver checked-into lib/ directory) - if you're on a different version of chrome (or not on Windows) let me know
driver = webdriver.Chrome(executable_path='lib/chromedriver.exe')
driver.get(agreeurl)
driver.find_element_by_name("action-I Agree").click()

if debug: print("> Clicked I Agree Button")

# Now we're on the D77 page, click the Send button to be issued a session ID
driver.find_element_by_name("action-Send").click()
if debug: print("> Clicked Send Button")

# Grab the next URL (which contains the session ID) - we'll use this URL from now on
url = driver.current_url

if debug: print("> Got URL:\t\t" + url)

# Start a session
s = requests.Session()

# Grab the cookie info
cookies = driver.get_cookies()

# set the session cookies
for cookie in cookies:
    s.cookies.set(cookie['name'], cookie['value'])

# Close the selenium session and close the browser
driver.quit()

# --------------------------------------------------------------------------------
## Make data requests

# Create request log list
#requestLog = []

logPackage = {
    "geography"      : "",
    "geo_cd"         : "",
    "geo_desc"       : "",
    "year"           : "",
    "sex"            : "",
    "age"            : "",
    "race"           : "",
    "total_records"  : "",
    "unsuppressed"   : "",
    "message"        : ""
}

# Start the log file
rkeys = logPackage.keys()
rFile = open(requestLogFile, "w", newline='')
dict_writer = DictWriter(rFile, rkeys, delimiter="\t")
dict_writer.writeheader()

# Loop through our various queries (State, Age, Sex, etc.)
print()
print("> # of Iterations:\t" + str(len(iterations)))
print()

if TESTING :
    print("> TESTING MODE: Only testing first 10 iterations")
    print()
    iterations = iterations[:10]

for i,j in enumerate(iterations) :

    # Get Parameters for this request
    geo =  j[iterKey["geo"]]
    yr  =  j[iterKey["year"]]
    sex =  j[iterKey["sex"]]
    age =  j[iterKey["age"]]
    race = j[iterKey["race"]]

    # Print current iteration info
    status_msg = "Request: "+str(i+1)+"/"+str(len(iterations))+"\t|"

    for k in iterKey.keys() :
        status_msg = status_msg+"\t"+k+": "+str(j[iterKey[k]])
    
    print(status_msg)

    # Set the parameters in the request Data package
    requestData["F_D77.V9"] = geo
    requestData["F_D77.V1"] = yr
    requestData["V_D77.V7"] = sex
    requestData["V_D77.V5"] = age
    requestData["V_D77.V8"] = race

    # Create the log package
    if GEO_COUNTY :
        geo_lvl  = "COUNTY"
    else :
        geo_lvl  = "STATE"

    logPackage = {
        "geography"      : geo_lvl,
        "geo_cd"         : geo,
        "geo_desc"       : geos[geo],
        "year"           : yr,
        "sex"            : sex,
        "age"            : age,
        "race"           : race,
        "total_records"  : 0,
        "unsuppressed"   : 0,
        "message"        : ""
    }

    # Wait between calls
    if REQUEST_SLEEP : time.sleep(1)

    #print(json.dumps(requestData, indent=4))

    # Make the request
    if debug: print("> Making Data Request")
    r = s.post(url, data=requestData)
    if debug: print("> Reponse:\t"+ str(r.status_code), r.reason)

    # See if we got a good file name
    filename = get_filename_from_cd(r.headers.get('content-disposition'))
    expectedFilename = "Multiple Cause of Death, 1999-2017.txt"

    if (filename != expectedFilename) :
        
        # If we didn't get a valid file - we probably exceeded the 75k record threshold - Add it to the log
        msg = "Exceeded 75k records - logging query parameters"
        logPackage["message"] = msg
        #requestLog.append(logPackage)
        dict_writer.writerow(logPackage)

        if debug: print("> "+msg)

    else :
        # If we got a valid file back, proceed...
        if debug: print("> Got Filename:\t" + filename)

        # Grab the file that was returned, convert to a string, get rid of double quotes, and load into an array
        open("debug_file.txt", 'wb').write(r.content)
        responseData = r.content.decode('utf-8').replace('"','').splitlines()

        # Grab the Header
        header=re.split(r'\t+',responseData[0])

        # Remove the header from the data
        responseData.pop(0)

        # Convert the array of data into a dataframe
        df = pd.DataFrame([sub.split("\t") for sub in responseData])
        
        # If we got no results back:
        if(df.empty or len(df.columns)==1) :

            msg = "No Data Records Returned"
            logPackage["message"] = msg
            #requestLog.append(logPackage)
            dict_writer.writerow(logPackage)
            
            if debug: print("> "+msg)

        else :
            df.columns = header

            # Filter out records with a Note - the data records don't have a note
            df = df[df['Notes'] == ""]

            # Grab the total number of data records and add it to the log
            logPackage["total_records"] = len(df)

            # Grab the number of unsupressed records
            logPackage["unsuppressed"] = len(df[df['Deaths'] != "Suppressed"])
            
            if debug: print("> Got "+ str(logPackage["total_records"]) +" total records and "+ str(logPackage["unsuppressed"]) +" unsuppressed records\n")

            # Add fields to the DF to store meta data
            if GEO_COUNTY :
                df["State_Code"] = ""
                df["State"] = ""
                df["County Code"] = geo
                df["County"] = geos[geo]
            else : # Don't add county code fields as the groupby adds them already
                df["State_Code"] = geo
                df["State"] = geos[geo]
            
            if GROUP_YEARS :
                df["Year"] = ",".join(yr)
            else :
                df["Year"] = yr
            df["Sex"] = sex
            df["Age"] = age
            df["Race_Code"] = race
            df["Race"] = races[race]

            # Write the dataframe results to a file
            outFile = outDir+geo+"/results_"+str(i)+".tab"
            df.to_csv(outFile, sep="\t", index=False,  encoding='utf-8')

            # Log the result
            msg = "Successful"
            logPackage["message"] = msg
            #requestLog.append(logPackage)
            dict_writer.writerow(logPackage)

'''
if debug:
    print()
    print("> Request Log:")
    print(requestLog)
    print()
    print("> Writing Log to File: "+requestLogFile)
    print()


# Write request log to file
rkeys = requestLog[0].keys()
with open(requestLogFile, "w", newline='') as f:
    dict_writer = DictWriter(f, rkeys, delimiter="\t")
    dict_writer.writeheader()
    for val in requestLog:
        dict_writer.writerow(val)
'''