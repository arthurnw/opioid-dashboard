
import requests
import xml.etree.ElementTree as ET
import re
from pprint import pprint
#import todo

# URL Info
baseURL = "https://wonder.cdc.gov/controller/datarequest/"
dbID = "D76"
url = baseURL + dbID

# Input Request
#requestXML = "requests/example1.xml" # Example 1 from CDC Wonder API - Multiple counts by Year / ethnicity
requestXML = "requests/example2.xml" # Example 2 from CDC Wonder API - Injury Intent and Mechanism, age < 18
#requestXML = "requests/test_request.xml"

# Output response file (to write)
outXML = "response.xml"

# If true, issues API request. If False, skips request and uses previous request results in outXML
requestData = True
#requestData = False

# Enable more logging
debug = True
#debug = False

if debug :
    print()
    print("----------------------------------")

    if(requestData) :
        print("Making Request:")
        print()
        print("URL:\t\t" + url)
        print("Request:\t" + requestXML)
    else :
        print("Reusing Request Response:")
        print()

    print("Reponse:\t" + outXML)
    print("----------------------------------")
    print()

# --------------------------------------------------------------------------------
## Functions

# Function to make the API request to CDC Wonder API
def makeRequest():

    # Assemble the package
    parameters = {  "request_xml": open(requestXML).read(),
                    "accept_datause_restrictions": "true"
                }

    # Make the request
    resp = requests.post(url, data=parameters)

    if debug: print("Response:\t" + str(resp.status_code))

    if resp.status_code != 200:
        # This means something went wrong.
        print("Received Error Response:\t" + str(resp.status_code)+ "\t" + str(resp.reason) + "\t" + str(resp.text))

    # Print XML response to file
    myOutFile = open(outXML, "wb")
    myOutFile.write(resp.content)

# Parse the data table portion of the XML
def parseDataTable(dt):

    return 0


# Parse the XML to get the data we want
def parseXML(xmlfile): 
  
    # create element tree object 
    tree = ET.parse(xmlfile) 
  
    # get root element 
    root = tree.getroot() 
  
    # Get the list of values that are being returned (these are codes - need to be translated to real column names)
    dataCols = []

    for m in root.findall("./response/options/measure-selections-show/") :
        #print(m.tag, m.attrib)
        measure = m.get('code')
        dataCols.append(measure)

    if debug: 
        print("Data Column Codes:")
        print(dataCols)
        print()
  

    

    # Grab the entire block of data results
    #datatable = ET.tostring(root.find("./response/data-table"))
    #print(datatable)

    # create empty list to store data records
    dataset = []

    # Loop through the data table, clean up the records, add to the array
    for r in root.findall("./response/data-table/r") :
        dt = re.sub(r'<\/*r>','',ET.tostring(r).decode('UTF-8'))
        dt = re.sub(r'\n','',dt)
        dataset.append(dt)

    if debug: 
        print("Data Table Lines:")
        print("\n".join(dataset))

    return dataset

# --------------------------------------------------------------------------------
## Main

# If we want to fetch new data, make the request
if(requestData) : makeRequest()

# Parse the XML
parseXML(outXML)

# ... profit
