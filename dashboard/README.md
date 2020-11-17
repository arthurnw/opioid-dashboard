
# Installing Dash

Pre-req:
* python v.3.7.x

Install Dash:
* pip install dash==1.4.1
* pip install dash-daq==0.2.1

After running the above, you should be able to run the example dash application:

    python example.py
    
    Open your browser and visit http://127.0.0.1:8050/


# Installing geopandas, pyshp, shapely and dependencies

### Unix-based OS (MacOS, Linux, etc.):
    This should be easy:

    pip install geopandas
    pip install pyshp
    pip install shapely
    pip install plotly-geo

    Once everything is installed, try running the following from the dashboard directory to confirm things are working:

        python example2.py
    
    This should launch an example choropleth dashboard in your browser

### Windows:

    Not as easy - there are dependencies that don't install well on Windows...

    There are several library wheels that you need to install manually.
    I've already downloaded these from the location below and placed them in the lib/ directory.

        https://www.lfd.uci.edu/~gohlke/pythonlibs/

    
    Install each of the packages listed below (in order) from the wheel files in the lib directory:
    
        Open a command prompt and navigate to the jakewama/lib directory
        
        pip install <file>.whl

        ** Note 1: If you have any of these packages installed already, you may need to uninstall first.
        ** Note 2: If you have an AMD processor, use the files with AMD in the name, otherwise, use the win32 files.

        GADL
        Fiona
        pyproj
        rtree
        shapely

    Add the GADL osgeo to your windows path:

        C:\<path to python install>\Python37-32\Lib\site-packages\osgeo

    Open a new command prompt (so it sees the change in path) and type the following to confirm GADL is working properly:

        gdalinfo --version
    
    You should see:

        GDAL 3.0.2, released 2019/10/28
        
    Now you can install geopandas and pyshp:

        pip install geopandas
        pip install pyshp
        pip install plotly-geo

    Once everything is installed, try running the following from the dashboard directory to confirm things are working:

        python example2.py
    
    This should launch an example choropleth dashboard in your browser