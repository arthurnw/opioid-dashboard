*** Overview ***
This README outlines the scripts and datasets contained in the "CODE/acquisition" folder. There are two main python scripts:

1. CDC Wonder Scraper 	(cdc_multi_cod_scraper.py)
2. Data Harmonizer		(data_harmonizer.py)

These two scripts handle the acquisition of the primary data source (CDC Wonder) as well as the harmonization of that data source with numerous county and state-level demographic data files we acquired.

The additional data sources were not included in this package due to size constraints. We have listed the data sets used and their location in the Final Report.

*** CDC Wonder Scraper ***
The python script "cdc_multi_cod_scraper.py" is a web-scraping application used to gather data from the CDC Wonder application, located here:

https://wonder.cdc.gov/mcd-icd10.html

The script leverages web-scraping as well as POST requests to pull opioid-related mortality data from CDC Wonder in an iterative fashion.

** Pre-Requisites **
The following pre-requisites must be met to run this application:

* Python 3.7
* Chrome 77 or higher

Required Python libraries:
* requests
* selenium
* re
* pandas
* json
* csv
* os
* sys
* time

** Running the script **
The script is setup to run as-is. There are numerous options and toggles at the top of the script that allow for different settings when acquiring the data. These are set to the proper settings for the data set we used.

To run the script:
1. Ensure you have satisfied the pre-reqs above and have unzipped this final code package to its own directory.
2. Open a command prompt and navigate to the "CODE/acquisition" folder
3. Run the following: python .\cdc_multi_cod_scraper.py

** Output **
The script will create state-specific (numbered) folders in the "CODE/acquisition/cdc_mcd_data/" directory. Inside each state folder will three tab-delimited files, one for each year-grouping we used (2000-2005, 2006-2011, 2012-2017).

** Next steps **
We then concatenated all of these tab-delimited files together to create a single tab-delimited file, called "ALL_US_6yr_adj.tab", which we placed in the "data_raw" directory.

*** Data Harmonizer ***
The python script "data_harmonizer.py" is a data harmonization script that takes in numerous data sources, cleans them up, merges them together, and outputs the data needed for several different aspects of the project, including:

* Prediction
* Visualization:
	* Investigation View Choropleth
	* Investigation View sub plots
	* Prediction View Choropleth
	
** Pre-Requisites **

* Python 3.7

Required Python libraries:
* pandas
* numpy

** Data Dependencies **
There are numerous data sets that need to be located in the "CODE/acquisition/data_raw" folder for this script to run properly, including the output of the CDC Wonder Scraper above. As mentioned before, most of the ancillary demographic data sets were not included because of size limitations, which means the script won't run on its own until those dependencies are satisfied.

** Running the script **

To run the script:
1. Ensure you have satisfied the pre-reqs and data depenencies above and have unzipped this final code package to its own directory.
2. Open a command prompt and navigate to the "CODE/acquisition" folder
3. Run the following: python .\data_harmonizer.py

** Output **
The script will generate several harmonized data sets in the "CODE/acquisition/data_clean" folder, including:

1. cdc.tab						# Cleaned up version of the CDC Wonder data
2. prediciton_input.tab			# Input to the prediction algorithm code
3. map_input.tab				# Data used for the Visualization: Investigation View Choropleth
4. prediction_map_input.tab		# Data used for the Visualization: Prediction View Choropleth
5. subplot_input.tab			# Data used for the Visualization: Investigation View Sub Plots


