***DESCRIPTION***
This package contains a web application to visualize opioid-related mortality data.

It contains:
- HTML pages (and associated stylesheet)
- d3.js code
- Data used in visualizations

The data sets included in the package and used by the visualization have been heavily pre-processed from numerous, large data sources to get to a streamlined, harmonized set of data that is more efficient for the application.

A list and description of the data used has been included in the Final Report and the code for acquiring and processing the data can be found in the "acquisition" folder, located in the CODE directory of this package.


***INSTALLATION***
You must be able to launch a simple web server on your machine in order to execute this code, as the code reads a file from the extracted .ZIP.

We recommend using Python's http module, which is part of the standard library. Beyond being able to launch a web server, no special installation is required. 

The code references standard d3.js libraries, so an internet connection is required to run the application. Aside from that, all required data and code is included in the .ZIP archive. 

Unzip the archive into a directory of your choice.


***EXECUTION***

To launch the web application:
1. Launch a command line prompt/terminal window
2. In the command line/terminal, navigate to the the CODE subfolder inside the directory containing the unzipped files (e.g. `cd C:\team30final\CODE`)
3. Launch a web server from this directory (e.g. `python -m http.server 8888`)
4. Launch a web browser of your choice (we recommend Chrome or Firefox) and connect to your local web server (e.g. `localhost:8888`)

Execution Demo Video: https://youtu.be/I-G7U3bLfuY

Using the application:
The application is broken into two primary views: Investigation and Prediction:

1. The Investigation View allows users to investigate the historical and current demographic and opioid mortality rate data at a state and county level.
2. The Prediction View allows users to explore future opioid mortality rate predictions based on demographic features at a county level for 2018-2013.

There are different data metrics and year ranges a user can select on the left navigation bar, which will refresh the choropleth with relevant data for the selected navigation panel parameters. Instructions for using the choropleth are also located on the left navigation bar.

In the Investigation View, zooming into a state (by double-clicking on it) allows for visualization at the county-level. Single-clicking a county will render the visualizations below the choropleth, giving further insight into the selected metric over time as well as the demographic makeup of the county population. Double-clicking the same state in the choropleth map will zoom back out to the country-wide view or double-clicking an adjacent state will move the zoomed-view to that new state.

In the Prediction View, you can also zoom into a state by double-cliking to see county-level predicted metrics for 2018-2023. Below the choropleth is a heatmap showing the correlation between predictors and response that we observed when training the predictive algorithm. Double-clicking the same state in the choropleth map will zoom back out to the country-wide view or double-clicking an adjacent state will move the zoomed-view to that new state.
