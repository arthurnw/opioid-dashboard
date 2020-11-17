
// Main svg parameters
var width = 700
var height = 350
var padding = 20

// Subplot Left parameters
var spl_width = 500
var spl_height = 250
var spl_margin = {top: 5, right: 100, bottom: 90, left: 120}

// Which field to use as the response
var years = ['2024']
var yr = '2024'
var yrLabel = '2018 - 2023'
var responseMetric = 'deaths_age_adj'
var metricLabel = "Age-Adjusted Deaths"
var responseField = responseMetric + "_" + yr
var populationField = "population_" + 2017
var zoom = 'us'
var sid = ''
var ctyID = ''      // will hold the user-clicked ctyID
var ctyLabel = ''    // will hold the user-clicked county label

// Number of color steps to use
var littleSteps = 4
var bigSteps = 4
var steps = littleSteps
var colorCodes = d3.schemeBlues[steps];

// Legend Params
var legendBlockHeight = 25;
var legendBlockWidth = 25;
var legend_width  = 150
var legend_height = 125

/* ------------------------------------------------------------------ */
// Main map

//var dataScale = d3.scaleLog().clamp(true)
var dataScale = d3.scaleLinear()

// Main Map SVG scales
var color = d3.scaleQuantile()
      .range(colorCodes)

var projection = d3.geoAlbers()
    .precision(0)
    .scale(height * 2).translate([width / 2, height / 2])

var path = d3.geoPath().projection(projection)

// Create main map svg
var svg = d3.select("#map_container")
    .append('svg')
    .attr("viewBox", "0 0 "+width+" "+height)

/* ------------------------------------------------------------------ */
// Subplot Left

var spl_ranges = ["Age, Gender", "Ethnicity", "Edu, Pov, Income, Unempl"];

// initialize first range and number of steps for heatmap
var spl_currentRangeIndex = 0;
    spl_steps = 6

function spl_filter_data(data, string){
    return data.filter(function(a){return a.Dem_Grouping == string})
  };

function spl_range(start, stop, step) {
    if (typeof stop == 'undefined') {
        // one param defined
        stop = start;
        start = 0;
    }

    if (typeof step == 'undefined') {
        step = 1;
    }

    if ((step > 0 && start >= stop) || (step < 0 && start <= stop)) {
        return [];
    }

    var result = [];
    for (var i = start; step > 0 ? i < stop : i > stop; i += (stop/step)) {
        result.push(i);
    }

    return result;
};

var spl_total_width = spl_width+spl_margin.left + spl_margin.right
var spl_total_height = spl_height+spl_margin.top + spl_margin.bottom

// Create left subplot SVG
var svg_left = d3.select("#heatmap_left")
    .append('svg')
    .attr("viewBox", "0 0 "+spl_total_width+" "+spl_total_height);

demo_labels = {
    'population'        : 'Population',
    'pct_male'          : '% Male',
    'pct_female'        : '% Female',
    'pct_white'         : '% White',
    'pct_black'         : '% African American',
    'pct_aina'          : '% Native American',
    'pct_apia'          : "% Asian",
    'pct_hispanic'      : "% Hispanic",
    'pct_15_19'         : '% Ages 15 - 19',
    'pct_20_24'         : '% Ages 20 - 24',
    'pct_25_29'         : '% Ages 25 - 29',
    'pct_30_34'         : '% Ages 30 - 34',
    'pct_35_39'         : '% Ages 35 - 39',
    'pct_hs_diploma'    : '% HS Diploma',
    'pct_bachelors'     : '% Bachelors',
    'pov_pct'           : '% in Poverty',
    'median_hh_inc'     : 'Median Household Inc',
    'unemploy_rate'     : 'Unemployment Rate',
    'deaths'            : 'Raw Death Count',
    'deaths_age_adj'    : 'Age-Adjusted Rate',
    'death_rate'        : 'Mean Deaths per 100k'
}

var hm_legend_width = 150;
    hm_legend_height = 250;

// Create legend SVG
var svgHeatMapLegend = d3.select("#heatmap_right")
    .append('svg')
    .attr('width', hm_legend_width)
    .attr('height', hm_legend_height)

/* ------------------------------------------------------------------ */
// Create Map legend SVG
var svgLegend = d3.select("#map_legend")
    .append('svg')
    .attr('width', legend_width)
    .attr('height', legend_height)

// Create Tooltips
var tip = d3.tip().attr('class', 'd3-tip').direction('e').offset([0,5])
.html(function(d) {
    if(responseMetric == "deaths") {
        metricFormat = ",.0f"
    }
    else{
        metricFormat = ".2f"
    }
    var content = "<span style='margin-left: 2.5px;'><b>" + d.properties.label + "</b></span><br>";

    if(isNaN(d.properties[populationField]) | d.properties[populationField] ==0 ) {
        var pop = "Not Available";
    }
    else {
        pop = d3.format(",.0f")(d.properties[populationField])
    }

    var met1 = d.properties[responseMetric + "_" + 2000];
        met2 = d.properties[responseMetric + "_" + 2010];
        met3 = d.properties[responseMetric + "_" + 2017];
        met4 = d.properties[responseMetric + "_" + 2024];

    if(isNaN(met1)) {
        met1    = "Not Available";
    }
    else {
        met1    = d3.format(metricFormat)(met1);
    }
    if(isNaN(met2)) {
        met2    = "Not Available";
    }
    else {
        met2    = d3.format(metricFormat)(met2);
    }
    if(isNaN(met3)) {
        met3    = "Not Available";
    }
    else {
        met3    = d3.format(metricFormat)(met3);
    }
    if(isNaN(met4)) {
        met4    = "Not Available";
    }
    else {
        met4    = d3.format(metricFormat)(met4);
    }


    //console.log(d.id, pop, d.properties.label, met)
    content +=`
        <table style="margin-top: 2.5px;">
                <tr><td>Population (2017) </td><td style="text-align: right">` + pop + `</td></tr>
                <tr><td></td><td></td></tr>
                <tr><td><b>`+metricLabel+`</b></td><td style="text-align: right"></td></tr>
                <tr><td>2000-2005</td><td style="text-align: right">` + met1 + `</td></tr>
                <tr><td>2006-2011</td><td style="text-align: right">` + met2 + `</td></tr>
                <tr><td>2012-2017</td><td style="text-align: right">` + met3 + `</td></tr>
                <tr><td>2018-2023 (Predicted)</td><td style="text-align: right">` + met4 + `</td></tr>
        </table>
        `;
    return content;
});
svg.call(tip);

var heatMapTip = d3.tip()
    .attr('class', 'd3-hm-tip')
    .direction('e')
    .offset([0,5])
    .html(function(d) {

        metricFormat = ".2f"

        var content =`
            <table style="margin-top: 2.5px;">
                    <tr><td><b>Metric</b></td><td style="text-align: right">`+demo_labels[d.Metric]+`</td></tr>
                    <tr><td><b>Predictor</b></td><td style="text-align: right">`+demo_labels[d.Feature]+`</td></tr>
                    <tr><td><br></td><td></td></tr>
                    <tr><td><b>Correlation Coef</b></td><td style="text-align: right">` + d3.format(metricFormat)(d.Value) + `</td></tr>
            </table>
            `;
        return content;
    });

// List of files to be read in
var promises = [
    d3.tsv('data/prediction_map_input.tab', function(d) {
        return {
            id: +d.fips,
            state: d.state,
            county: d.county,
            label : d.label,
            population_2000 : +d.population_2000,
            population_2010 : +d.population_2010,
            population_2017 : +d.population_2017,
            deaths_2000 : +d.deaths_2000,
            deaths_2010 : +d.deaths_2010,
            deaths_2017 : +d.deaths_2017,
            md_per_100k_2000 : +d.md_per_100k_2000,
            md_per_100k_2010 : +d.md_per_100k_2010,
            md_per_100k_2017 : +d.md_per_100k_2017,
            md_per_100k_2024 : +d.md_per_100k_2024,
            deaths_age_adj_2000 : +d.deaths_age_adj_2000,
            deaths_age_adj_2010 : +d.deaths_age_adj_2010,
            deaths_age_adj_2017 : +d.deaths_age_adj_2017,
            deaths_age_adj_2024 : +d.deaths_age_adj_2024
        }
    }),
    d3.json('data/us-states.json'),
    d3.json('data/us-counties.json'),
    d3.csv("data/correlation_data.csv")
]
Promise.all(promises).then(initialize)

function initialize(results) {

    //console.log(results)

    var data = results[0]
    var states = topojson.feature(results[1], results[1].objects.states).features
    var counties = topojson.feature(results[2], results[2].objects.counties).features
    var corrData = results[3]

    var spl_long_data = [];
    corrData.forEach( function(row) {

        // Loop through all of the columns, and for each column, make a new row
        Object.keys(row).forEach( function(colname) {

            // Ignore 'States', 'Category' and 'Value' columns
            if(colname == "Features" || colname == "Value" || colname == "Dem_Grouping") {
                return
            }
            spl_long_data.push({"Feature"   : row["Features"],
                            "Dem_Grouping"  : row["Dem_Grouping"],
                            "Value"         : +row[colname],
                            "Metric"        : colname});
        });
    });

    //console.log(spl_long_data)
    //console.log(data)

    // Grab the selection from the Data Metric dropdown
    d3.select('#selectMetric')
    .on("change", function () {
        var metricSect = document.getElementById("selectMetric");
        metricBundle = JSON.parse(metricSect.options[metricSect.selectedIndex].value);

        responseMetric  = metricBundle['metric']
        metricLabel     = metricBundle['label']
        responseField   = responseMetric + "_" + yr

        if(zoom == 'us') {
            usZoom();
        }
        else {
            svg.selectAll('.county')
                .remove()
            stateZoom(sid)
        }
        metricDesc()
    });

    d3.select('#selectHeatmap')
    .on("change", function () {

        var heatSect = document.getElementById("selectHeatmap");
        selected_range = JSON.parse(heatSect.options[heatSect.selectedIndex].value);

        //console.log("Updating heatmap",selected_range)
        spl_currentRangeIndex = +selected_range;

        subLeft()
    });

    states.forEach(function (f) {
        f.properties = data.find(function (d) { return d.id === f.id })
    })

    counties.forEach(function (f) {
        f.properties = data.find(function (d) { return d.id === f.id }) || {}
    })

    metricDesc()
    reScale(states)

    var statePaths = svg.selectAll('.state')
        .data(states)
        .enter().append('path')
        .attr('class', 'state')
        .attr('d', path)
        .style('fill', function (d) { return color(dataScale(d.properties[responseField])) })
        .on('dblclick', function (d) { stateZoom(d.id) })
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);

    // Draw the sub plots
    subLeft()

    function reScale(data) {
        /*
        Rescales the choropleth and triggers a redraw of the legend
        */

        // Get current data min and max
        min = d3.min(data, function(d) { props = d.properties; return props[responseField];})
        max = d3.max(data, function(d) { props = d.properties; return props[responseField];})

        //console.log("Scaling",responseField, min, max, steps)

        if(min==0) {
            min=0.0001
        }

        colorCodes = d3.schemeBlues[steps];

        dataScale.domain([min,max]).range([0,50])
        color.domain(dataScale.range()).range(colorCodes)

        drawLegend(min,max)

    }

    function drawLegend(min,max) {

        // Ditch the legend if exists and redraw
        svgLegend.selectAll(".legend").remove();

        legendHeader = d3.select("#map_legend")
        legendHeader.select("h4").remove();
        legendHeader.select("h5").remove();
        legendHeader.insert("h5",":first-child").text(metricLabel)
        legendHeader.insert("h4",":first-child").text(yrLabel);

        colorQuantiles = color.quantiles();
        colorQuantiles.unshift(0);

        //console.log(colorQuantiles)

        svgLegend
            .append("g")
            .attr("class", ".legend")

        var legend = svgLegend.selectAll(".legend")
            .data(colorQuantiles)
            .enter()
            .append("g")
            .attr("class", "legend")
            .attr("transform", function(d, i) {
                return ("translate(0," + i * legendBlockWidth + ")")
                })
            ;

        legend.append("rect")
            .attr("x", 25)
            .attr("y", 0)
            .attr("width", legendBlockWidth)
            .attr("height", legendBlockHeight)
            .style("fill", function(d, i) {
                return (colorCodes[i]);
            });

        legend.append("text")
            .attr("x", (legend_width * .65))
            .attr("y", legendBlockHeight * .7 )
            .text(function(d, i) {
                //console.log(i, colorQuantiles[i], colorQuantiles[i].toFixed(0));

                rangeMin = Math.floor(dataScale.invert(colorQuantiles[i]));

                if(i==0) {
                    rangeMin = 0;
                }

                // Handle the case where it's the last legend region
                if(i==colorQuantiles.length-1) {
                    rangeMax = Math.ceil(max);
                }
                else {
                    rangeMax = Math.floor(dataScale.invert(colorQuantiles[i+1]));
                }

                // Handle the case where the region min and max are the same
                if(rangeMin == rangeMax) {
                    rangeLabel = rangeMin;
                }
                else {
                    rangeLabel = rangeMin + " - " + rangeMax;
                }
                return rangeLabel;

            })
            .style("text-anchor", "middle");

            updateZoomDesc();

    }

    function updateZoomDesc () {
        header = d3.select("#map_legend")
        header.select("p").remove();

        if(zoom == 'us') {
            txt = '* <i>Scaled to country min/max<br>across all US States</i> <br><br> * <i>State-Level data represents the mean of county-level predictions</i>';
        }
        else {
            txt = '* <i>Scaled to country min/max<br>across all US Counties</i>';
        }
        header.insert("p").html(txt)
    }

    function usZoom() {
        var t = d3.transition().duration(800)
        zoom = 'us'
        steps = littleSteps
        reScale(states)

        projection.scale(height * 2).translate([width / 2, height / 2])

        statePaths.transition(t)
            .attr('d', path)
            .style('fill', function (d) { return color(dataScale(d.properties[responseField])) })

        svg.selectAll('.county')
            .data([])
            .exit().transition(t)
            .attr('d', path)
            .style('opacity', 0)
            .remove()
    }

    function stateZoom(id) {
        zoom = 'state'
        sid = id

        steps = littleSteps

        reScale(counties)

        var state = states.find(function (d) { return d.id === id })
        var stateCounties = counties.filter(function (d) {
            return d.id > id && d.id < id + 1000
        })

        var t = d3.transition().duration(800)

        var countyPaths = svg.selectAll('.county')
            .data(stateCounties, function (d) { return d.id })

        var enterCountyPaths = countyPaths.enter().append('path')
            .attr('class', 'county')
            .attr('d', path)
            .style('fill', function (d) { val = d.properties[responseField]; if(val==0){ val = 0.01;} return color(dataScale(val)) })
            .style('opacity', 0)
            .on('dblclick', function () { usZoom() })
            .on('click', function(d) {
                ctyID = d.id;
                ctyLabel = d.properties['label'];
                //countyName()
                //subLeft()
                //subRight()
            })
            .on('mouseover', tip.show)
            .on('mouseout', tip.hide);

        projection.fitExtent(
            [[padding, padding], [width - padding, height - padding]],
            state
        )

        statePaths.transition(t)
            .attr('d', path)
            .style('fill', '#444')

        enterCountyPaths.transition(t)
            .attr('d', path)
            .style('opacity', 1)

        countyPaths.exit().transition(t)
            .attr('d', path)
            .style('opacity', 0)
            .remove()
    }

    function metricDesc() {
        /*
        Updates the metric description in the nav bar
        */
        if(responseMetric == 'deaths') {
            var desc = "Simple count of the number of opioid-related deaths. Counties with <10 deaths are suppressed by the CDC's WONDER system, so we have imputed values between 0 and 9, proportional to those counties' populations."
        }
        else if(responseMetric == 'deaths_age_adj') {
            var desc = "Weighted average of age-group-specific mortality rates for each county, allowing comparisons across counties with different age group distributions. Age adjustment is commonly used by the CDC and other researchers."
        }
        else {
            var desc = 'Captures mortality rate, adjusted for population, averaged for a given six-year time period. The "crude rate" is a metric reported by the CDC, calculated as deaths / population * 100,000 for a single year.'
        }
        d3.select("#metricDesc").text(desc)
    }

    function subLeft() {
        /*
        Function to create the left subplot
        */

        // Ditch the subplot if it exists and redraw
        svg_left.selectAll(".subplot_left").remove();
        d3.selectAll("class","d3-hm-tip").remove();

        // Dynamically create the chart header
        header = d3.select("#heatmap_left")
        header.select("h4").remove();
        chart_title = "Correlation Heatmap for [" + spl_ranges[spl_currentRangeIndex] + "] Predictors"
        header.insert("h4",":first-child").text(chart_title)

        drawHeatMap()
        svg_left.call(heatMapTip);
    }

    function drawHeatMap() {

        // Filter down the data
        var heatmap_data = spl_filter_data(spl_long_data,spl_ranges[spl_currentRangeIndex])

        hm_min = d3.min(heatmap_data.map(d => d.Value));
        hm_max = d3.max(heatmap_data.map(d => d.Value));
        hm_range = spl_range(0, hm_max, spl_steps);

        g = svg_left
            .append("g")
            .attr("transform","translate(" + spl_margin.left + "," + spl_margin.top + ")")
            .attr("class", "subplot_left");

        // Labels of row and columns -> unique identifier of the column called 'group' and 'variable'
        var predictors = d3.map(heatmap_data, function(d){return d.Feature;}).keys()
        var mets = d3.map(heatmap_data, function(d){return d.Metric;}).keys()

        // Build X scales and axis:
        var spl_x = d3.scaleBand()
            .range([ 0, spl_width ])
            .domain(predictors)
            .padding(0.05);

        // Create the xaxis and map column names to human-readable
        var spl_xaxis = d3.axisBottom(spl_x)
            .tickFormat(function(d) { return demo_labels[d]})
            .tickSize(2)

        g.append("g")
            .attr("font-family", "sans-serif")
            .attr("font-size", 12)
            .attr("transform", "translate(0," + spl_height + ")")
            .call(spl_xaxis)
            .selectAll("text")
                .style("text-anchor", "end")
                .attr("dx", "-.8em")
                .attr("dy", ".15em")
                .attr("transform", "rotate(-45)");

        // Build Y scales and axis:
        var spl_y = d3.scaleBand()
            .range([ 0, spl_height ])
            .domain(mets)
            .padding(0.05);
        

        // Create the xaxis and map column names to human-readable
        var spl_yaxis = d3.axisLeft(spl_y)
            .tickFormat(function(d) { return demo_labels[d]})
            .tickSize(2)

        g.append("g")
            .attr("font-family", "sans-serif")
            .attr("font-size", 12)
            //.call(d3.axisLeft(spl_y).tickSize(2))
            .call(spl_yaxis)
            .select(".domain")

        // define the color palette to use for the heatmap
        spl_colors = ["#b2182b", "#ef8a62","#fddbc7","#d1e5f0","#67a9cf","#2166ac"]
        var colorScale = d3.scaleQuantize()
            .range(spl_colors)
            .domain([-1,1]);


        // add the squares
        g.selectAll()
            .data(heatmap_data, function(d) {return d.Feature+':'+d.Metric;})
            .enter()
            .append("rect")
                .attr("x", function(d) { return spl_x(d.Feature) })
                .attr("y", function(d) { return spl_y(d.Metric) })
                .attr("rx", 4)
                .attr("ry", 4)
                .attr("width", spl_x.bandwidth() )
                .attr("height", spl_y.bandwidth() )
                .style("fill", (d) => colorScale(d.Value))
                .style("stroke-width", 4)
                .style("stroke", "none")
                .style("opacity", 0.8)
                .on('mouseover',    heatMapTip.show)
                .on('mouseout',     heatMapTip.hide);

        // Draw the bar chart legend
        svgHeatMapLegend.selectAll(".legend").remove();

        var legend_box_size = 25
        var legend_labels = ['-1',' ',' ','0',' ','1']

        // Add legend
        var legend = svgHeatMapLegend
            .append("g")
            .attr("class","legend")
            .attr("transform","translate(0,"+15+")")
            .selectAll("rect")
            .data(spl_colors)
            .enter()
            .append("g")

        legend
            .append("rect")
            .attr("x",hm_legend_width/3)
            .attr("y",function(d,i){ return legend_box_size*2 + i*legend_box_size})
            .attr("width", legend_box_size)
            .attr("height", legend_box_size)
            .style("fill", function(d){ return d});

        legend
            .append("text")
            .attr("font-size", 12)
            .attr("x",hm_legend_width/2 + legend_box_size/2)
            .attr("y",function(d,i){ if(i==spl_colors.length-1) { return legend_box_size*3 + i*legend_box_size+5;} else { return legend_box_size*2 + i*legend_box_size + 5}})
            .attr('font-weight', 'normal')
            .style("text-anchor", "middle")
            .text(function(d,i){ return legend_labels[i]});

        // Add legend
        var legendText = svgHeatMapLegend
            .append("g")
            .attr("class","legend")

        legendText
            .append("text")
            .attr("x", 5)
            .attr("y", 45)
            .text("Negatively Correlated")
            .style("font-size", "12px");

        legendText
            .append("text")
            .attr("x", 5)
            .attr("y", 45*2 + legend_box_size * spl_steps)
            .text("Positively Correlated")
            .style("font-size", "12px")
    }
}
