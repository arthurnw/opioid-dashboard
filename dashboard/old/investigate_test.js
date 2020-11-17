console.log("Ready to create the map!");

// Update name of the response field to change it throughout
var responseField = "md_per_100k";

//var svg = d3.select("#map_container")
//        .append("svg")
//        .attr({
//            "width":mw,
//            "height":mh,
//        });

//var opiods = d3.map();
var mapData = {}

// Function to filter the data based on year and load it into a d3.map
function filterData(data, yr) {

    filt = data[yr];
    mmap = d3.map()

    filt.forEach(function(d){
        mmap.set(d.fips, +d.response);
    })
    
    return mmap
}

var promises = [
  d3.json("https://d3js.org/us-10m.v1.json"),
  d3.tsv("data/map_input.tab").then(function(mdata) { 
    
    mdata.forEach(function(d,i){
        
        if (! (d.year in mapData)){
            mapData[d.year] = []
        }
        mapData[d.year].push( { fips: d.fips, response : d[responseField]})

    })
  })
]

Promise.all(promises).then(ready)

function ready([us]) {

    //console.log(mapData)

    //filtMapData = filteredData(mapData,"2000");

    //console.log("Filtered data:")
    //console.log(filtMapData);

    showMap(us)
}

function showMap(us) {

    var opioids = filterData(mapData, "2000");

    var dmin = d3.min(opioids.values())
        dmax = d3.max(opioids.values())

    console.log(dmin, dmax)

    var svg = d3.select("#map")
        .style("width", "100%")
        .style("height", "auto");
    var width = +svg.attr("width");
    var height = +svg.attr("height");

    var steps = 9;
    var breaks = d3.range(0, steps).map(function(d){ return d / (steps - 1); });

    var quantize = d3.scaleQuantize()
        .domain([dmin, dmax])
		.range(d3.schemeBlues[9]);

    var path = d3.geoPath();
        
    var color = d3.scaleThreshold()
        .domain(d3.range(0, dmax))
        .range(d3.schemeBlues[9]);
    
    var length = color.range().length;

    var x = d3.scaleLinear()
        .domain(breaks)
        .range(d3.schemeBlues[9]);

    var g = svg.append("g")
        .attr("class", "key")
        .attr("transform", "translate(0,40)");
    
    g.selectAll("rect")
        .data(color.range().map(function(d) {
            d = color.invertExtent(d);
            if (d[0] == null) d[0] = x.domain()[0];
            if (d[1] == null) d[1] = x.domain()[1];
            return d;
        }))
        .enter().append("rect")
        .attr("height", 8)
        .attr("width", 215)
        .attr("x", function(d) { return x(d[0]); })
        .attr("width", function(d) { return x(d[1]) - x(d[0]); })
        .attr("fill", function(d) { return color(d[0]); });
    
    g.append("text")
        .attr("class", "caption")
        .attr("x", x.range()[0])
        .attr("y", -6)
        .attr("fill", "#000")
        .attr("text-anchor", "start")
        .attr("font-weight", "bold")
        .text("Opioid-Related Deaths");
    
    g.call(d3.axisBottom(x)
        .tickSize(13)
        .tickFormat(function(x, i) { return i ? x : x; })
        .tickValues(color.domain()))
        .select(".domain")
        .remove();

    svg.append("g")
        .attr("class", "counties")
      .selectAll("path")
      .data(topojson.feature(us, us.objects.counties).features)
      .enter().append("path")
        .attr("fill", function(d) { return color(d.response = opioids.get(d.id)); })
        .attr("d", path)
      .append("title")
        .text(function(d) { return d.response; });
  
    svg.append("path")
        .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
        .attr("class", "states")
        .attr("d", path);
    
}