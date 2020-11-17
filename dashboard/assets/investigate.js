
// Main svg parameters
var width = 700
var height = 350
var padding = 20

// Subplot Left parameters
var spl_width = 500
var spl_height = 250
var spl_margin = {top: 20, right: 20, bottom: 30, left: 40}
//var spl_padding = spl_margin.right + spl_margin.left

// Subplot Right parameters
var spr_width = 300
var spr_height = 250
var spr_margin = {top: 20, right: 20, bottom: 30, left: 40}

// Which field to use as the response
var years = ['2000','2010','2017']
var yr = '2000'
var yrLabel = '2000 - 2005'
var responseMetric = 'deaths_age_adj'
var metricLabel = "Age-Adjusted Deaths"
var responseField = responseMetric + "_" + yr
var populationField = "population_" + yr
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

var spl_total_width = spl_width+spl_margin.left + spl_margin.right
var spl_total_height = spl_height+spl_margin.top + spl_margin.bottom

// Create left subplot SVG
var svg_left = d3.select("#subplot_left")
    .append('svg')
    .attr("viewBox", "0 0 "+spl_total_width+" "+spl_total_height)

// Liquid variable inputs based on selectors
var metric_input = 'deaths_age_adj';
var county_selection = '1001';

// Parse the date / time
var parseDate = d3.timeParse("%Y");

// Define scales
yrMin = parseDate(2000)
yrMax = parseDate(2017)
var spl_xScale = d3.scaleTime().range([spl_margin.left, spl_width-spl_margin.right]).domain([yrMin, yrMax]);
var spl_yScale = d3.scaleLinear().range([(spl_height-spl_margin.top), spl_margin.bottom]);
var spl_color = d3.scaleOrdinal(d3.schemeCategory10);

// Define axes
var spl_xAxis = d3.axisBottom().scale(spl_xScale);
var spl_yAxis = d3.axisLeft().scale(spl_yScale).ticks(4);

// Function to draw line(s)
var spl_line = d3.line()
    .x(function(d) { return spl_xScale(d.year); })
    .y(function(d) { return spl_yScale(d.metric_value); })
    //.defined(function(d) { return d.metric_value; });        // defined() method handles missing data (omits from visualizing)


/* ------------------------------------------------------------------ */
// Subplot Right

var spr_total_width = spr_width+spr_margin.left + spr_margin.right
var spr_total_height = spr_height+spr_margin.top + spr_margin.bottom

// Create right subplot SVG
var svg_right = d3.select("#subplot_right")
    .append('svg')
    .attr("viewBox", "0 0 "+spr_total_width+" "+spr_total_height)

demo_labels = {
    'population'        : 'Population',
    'tot_male'          : 'Males',
    'tot_female'        : 'Females',
    'wa'                : 'White',
    'ba'                : 'African American',
    'ia'                : 'Native American',
    'aa'                : "Asian",
    'h'                 : "Hispanic",
    'age_grp_4'         : '15 - 19',
    'age_grp_5'         : '20 - 24',
    'age_grp_6'         : '25 - 29',
    'age_grp_7'         : '30 - 34',
    'age_grp_8'         : '35 - 39',
    'pct_hs_diploma'    : '% HS Diploma',
    'pct_bachelors'     : '% Bachelors',
    'pov_pct'           : '% in Poverty',
    'median_hh_inc'     : 'Household Inc',
    'unemploy_rate'     : 'Unemployment Rt'
}

demo_hierarchy = {
    'gender' : { 'fields' : ['tot_male', 'tot_female'], 'label':'Gender','measure':'Population'},
    'ethnicity' : {'fields':['wa','ba','ia','aa','h'], 'label':'Ethnicity','measure':'Population'},
    'age' : {'fields':['age_grp_4','age_grp_5','age_grp_6','age_grp_7','age_grp_8'], 'label':'Age Group','measure':'Population'},
    'education' : {'fields':['pct_hs_diploma','pct_bachelors'], 'label':'Education','measure':'Percent'},
    'poverty' : {'fields':['pov_pct'], 'label':'Poverty','measure':'Percent'},
    'income' : {'fields':['median_hh_inc'], 'label':'Median Household Income','measure':'Dollars'},
    'unemployment' : {'fields': ['unemploy_rate'], 'label':'Unemployment Rate','measure':'Percent'}
}

var demo_groups = Object.keys(demo_hierarchy);
//console.log(demo_groups)

// Default demo grouping
var demoVal = 'age'

// The scale spacing the groups:
var spr_x0 = d3.scaleBand()
    .rangeRound([0, spr_width])
    .paddingInner(0.1);

// The scale for spacing each group's bar:
var spr_x1 = d3.scaleBand()
    .padding(0.05);

var spr_y = d3.scaleLinear()
    .rangeRound([spr_height, 0]);

var spr_z = d3.scaleOrdinal()

var bar_legend_width = 150;
    bar_legend_height = 100;

// Create legend SVG
var svgBarLegend = d3.select("#subplot_right_dropdown")
    .append('svg')
    .attr('width', bar_legend_width)
    .attr('height', bar_legend_height)


// Create legend SVG
var svgLegend = d3.select("#map_legend")
    .append('svg')
    .attr('width', legend_width)
    .attr('height', legend_height)

// Create Tooltips
var tip = d3.tip()
    .attr('class', 'd3-tip')
    .direction('e')
    .offset([0,5])
    .html(function(d) {
        if(responseMetric == "deaths") {
            metricFormat = ",.0f"
        }
        else{
            metricFormat = ".2f"
        }
        var content = "<span style='margin-left: 2.5px;'><b>" + d.properties.label + "</b> ("+yrLabel+")</span><br>";

        if(isNaN(d.properties[populationField]) | d.properties[populationField] ==0 ) {
            var pop = "Not Available";
        }
        else {
            pop = d3.format(",.0f")(d.properties[populationField])
        }

        if(isNaN(d.properties[responseField])) {
            met = "Not Available";
            invMet = "Not Available";
        }
        else {
            met     = d3.format(metricFormat)(d.properties[responseField]);
            invMet  = d3.format(".2f")(dataScale(d.properties[responseField]));
        }
        //console.log(d.id, pop, d.properties.label, met)
        content +=`
            <table style="margin-top: 2.5px;">
                    <tr><td>Population: </td><td style="text-align: right">` + pop + `</td></tr>
                    <tr><td>`+metricLabel+`: </td><td style="text-align: right">` + met + `</td></tr>
            </table>
            `;
        return content;
    });
svg.call(tip);

var lineTip = d3.tip()
    .attr('class', 'd3-hm-tip')
    .direction('e')
    .offset([0,5])
    .html(function(d) {

        metricFormat = ".2f"
        var content =`
            <table style="margin-top: 2.5px;">
                    <tr><td><b>Year</b></td><td style="text-align: right">`+d.year.getFullYear()+`</td></tr>
                    <tr><td><b>`+metricLabel+`</b></td><td style="text-align: right">`+d3.format(".2f")(d.metric_value)+`</td></tr>
           </table>
            `;
        return content;
    });


// List of files to be read in
var promises = [
    d3.tsv('data/map_input.tab', function(d) {
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
            deaths_age_adj_2000 : +d.deaths_age_adj_2000,
            deaths_age_adj_2010 : +d.deaths_age_adj_2010,
            deaths_age_adj_2017 : +d.deaths_age_adj_2017
        }
    }),
    d3.tsv('data/subplot_input.tab', function(d) {
        return {
            id: +d.fips,
            population_2000 : +d.population_2000,
            population_2010 : +d.population_2010,
            population_2017 : +d.population_2017,
            tot_male_2000 : +d.tot_male_2000,
            tot_male_2010 : +d.tot_male_2010,
            tot_male_2017 : +d.tot_male_2017,
            tot_female_2000 : +d.tot_female_2000,
            tot_female_2010 : +d.tot_female_2010,
            tot_female_2017 : +d.tot_female_2017,
            wa_2000 : +d.wa_2000,
            wa_2010 : +d.wa_2010,
            wa_2017 : +d.wa_2017,
            ba_2000 : +d.ba_2000,
            ba_2010 : +d.ba_2010,
            ba_2017 : +d.ba_2017,
            ia_2000 : +d.ia_2000,
            ia_2010 : +d.ia_2010,
            ia_2017 : +d.ia_2017,
            aa_2000 : +d.aa_2000,
            aa_2010 : +d.aa_2010,
            aa_2017 : +d.aa_2017,
            h_2000 : +d.h_2000,
            h_2010 : +d.h_2010,
            h_2017 : +d.h_2017,
            age_grp_4_2000 : +d.age_grp_4_2000,
            age_grp_4_2010 : +d.age_grp_4_2010,
            age_grp_4_2017 : +d.age_grp_4_2017,
            age_grp_5_2000 : +d.age_grp_5_2000,
            age_grp_5_2010 : +d.age_grp_5_2010,
            age_grp_5_2017 : +d.age_grp_5_2017,
            age_grp_6_2000 : +d.age_grp_6_2000,
            age_grp_6_2010 : +d.age_grp_6_2010,
            age_grp_6_2017 : +d.age_grp_6_2017,
            age_grp_7_2000 : +d.age_grp_7_2000,
            age_grp_7_2010 : +d.age_grp_7_2010,
            age_grp_7_2017 : +d.age_grp_7_2017,
            age_grp_8_2000 : +d.age_grp_8_2000,
            age_grp_8_2010 : +d.age_grp_8_2010,
            age_grp_8_2017 : +d.age_grp_8_2017,
            pct_hs_diploma_2000 : +d.pct_hs_diploma_2000,
            pct_hs_diploma_2010 : +d.pct_hs_diploma_2010,
            pct_hs_diploma_2017 : +d.pct_hs_diploma_2017,
            pct_bachelors_2000 : +d.pct_bachelors_2000,
            pct_bachelors_2010 : +d.pct_bachelors_2010,
            pct_bachelors_2017 : +d.pct_bachelors_2017,
            pov_pct_2000 : +d.pov_pct_2000,
            pov_pct_2010 : +d.pov_pct_2010,
            pov_pct_2017 : +d.pov_pct_2017,
            median_hh_inc_2000 : +d.median_hh_inc_2000,
            median_hh_inc_2010 : +d.median_hh_inc_2010,
            median_hh_inc_2017 : +d.median_hh_inc_2017,
            unemploy_rate_2000 : +d.unemploy_rate_2000,
            unemploy_rate_2010 : +d.unemploy_rate_2010,
            unemploy_rate_2017 : +d.unemploy_rate_2017,
            deaths_2000 : +d.deaths_2000,
            deaths_2010 : +d.deaths_2010,
            deaths_2017 : +d.deaths_2017,
            deaths_age_adj_2000 : +d.deaths_age_adj_2000,
            deaths_age_adj_2010 : +d.deaths_age_adj_2010,
            deaths_age_adj_2017 : +d.deaths_age_adj_2017,
            md_per_100k_2000 : +d.md_per_100k_2000,
            md_per_100k_2010 : +d.md_per_100k_2010,
            md_per_100k_2017 : +d.md_per_100k_2017
        }
    }),
    d3.json('data/us-states.json'),
    d3.json('data/us-counties.json')
]
Promise.all(promises).then(initialize)

function initialize(results) {

    //console.log(results)

    var data = results[0]
    var demoData = results[1]
    var states = topojson.feature(results[2], results[2].objects.states).features
    var counties = topojson.feature(results[3], results[3].objects.counties).features

    spl_color.domain(d3.keys(demoData))

    //console.log(demoData)

    // Grab the selection from the Year dropdown
    d3.select('#selectYear')
        .on("change", function () {
            var yrSect = document.getElementById("selectYear");
            yrBundle = JSON.parse(yrSect.options[yrSect.selectedIndex].value);

            yr              = yrBundle['year']
            yrLabel         = yrBundle['label']
            responseField   = responseMetric + "_" + yr

            if(zoom == 'us') {
                usZoom();
            }
            else {
                svg.selectAll('.county')
                    .remove()
                stateZoom(sid)
            }
    });

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
            metricDesc();
            subLeft()
    });

    d3.select('#selectDemo')
    .on("change", function () {
        var demoSect = document.getElementById("selectDemo");
        demoVal = demoSect.options[demoSect.selectedIndex].value;

        subRight();
    });

    //console.log("Data:")
    //console.log(data)

    states.forEach(function (f) {
        f.properties = data.find(function (d) { return d.id === f.id })
    })

    counties.forEach(function (f) {
        f.properties = data.find(function (d) { return d.id === f.id }) || {}
    })

    metricDesc()
    reScale(states)

    //console.log(counties)

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
    subRight()


    function reScale(data) {
        /*
        Rescales the choropleth and triggers a redraw of the legend
        */

        // Get current data min and max
        min = d3.min(data, function(d) { props = d.properties; return props[responseField];})
        max = d3.max(data, function(d) { props = d.properties; return props[responseField];})


        //console.log("Scaler:",min,max, steps)

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
            
            updateZoomDesc()
    }

    function updateZoomDesc () {
        header = d3.select("#map_legend")
        header.select("p").remove();

        if(zoom == 'us') {
            txt = '* <i>Scaled to country min/max<br>across all US States</i>';
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
                countyName()
                subLeft()
                subRight()
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

    function countyName() {
        /*
        Updates the county name between the choropleth and sub plots
        */
        //console.log("Update county: ",ctyLabel)
        header = d3.select("#brow")
        header.select("h3").text(ctyLabel)
    }

    function metricDesc() {
        /*
        Updates the metric description in the nav bar
        */
        if(responseMetric == 'deaths') {
            var desc = "Simple count of the number of opioid-related deaths. Counties with <10 deaths are suppressed by the CDC's WONDER system, so we have imputed values between 0 and 9, proportional to those counties' populations."
        }
        else if(responseMetric == 'deaths_age_adj') {
            var desc = "Weighted average of age-group-specific mortality rates for each county or state, allowing comparisons across counties or states with different age group distributions. Age adjustment is commonly used by the CDC and other researchers."
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

        header = d3.select("#subplot_left")
        header.select("h3").remove();
        header.select("h4").remove();

        chart_title = metricLabel + " Over Time"

        //console.log("SPL: ",ctyID, ctyLabel)

        if(ctyID) {
            //chart_title = ctyLabel + " " + chart_title
            sub_title = ctyLabel
            drawLineChart()

        } else {
            sub_title = 'Click a county to load data'
        }

        header.insert("h4",":first-child").text(chart_title)
        svg_left.call(lineTip);
    }

    function drawLineChart() {
        /*
        Function to draw the line chart
        */

        // remove existing content foromm the svg
        svg_left.selectAll("*").remove();

        svg_left
            .append("g")
            .attr("class", ".subplot_left")
            .attr("transform", "translate(" + spl_margin.left + "," + spl_margin.top + ")")



        var filtered_raw_data = demoData.filter(function(d) {
            return d.id == ctyID;
        })
        //console.log(filtered_raw_data)

        // Pivot the data (year columns to year columns)
        var metric_data = [];

        years.map(function(colYear) {
            f = responseMetric+"_"+colYear;
            for (var i = 0, len = filtered_raw_data.length; i < len; i++) {
                val = filtered_raw_data[i][f];
            }
            if(!(isNaN(val))) {
                metric_data.push({'id' : ctyID, 'year': parseDate(colYear), 'metric_value' : val})
            }
        })

        dmin = d3.min(metric_data, function(d) { return d.metric_value; })
        dmax = d3.max(metric_data, function(d) { return d.metric_value; })

        // No data to display
        if(dmax == 0) {

            svg_left
            .append("g")
            .attr("class","legend")
            .append("text")
            .attr("x", spl_total_width/4)
            .attr("y", spl_total_height/4)
            .text("No "+ metricLabel + " reported from 2000-2017")
            .style("font-size", "12px");

        }
        else {

            // Set the new domain
            spl_yScale.domain([0, dmax]);

            //console.log("Metrics:",metricCols)
            //console.log("Pivoted:", metric_data)
            //console.log(metric_data[0])

            // draw x-axis
            svg_left.append("g")
                .attr("class", "splx axis")
                .attr("transform", "translate(0," + (spl_height-spl_margin.top) + ")")
                .call(spl_xAxis);

            // draw y-axis
            svg_left.append("g")
                .attr("class", "sply axis")
                .attr("transform", "translate(" + spl_margin.left +", 0)")
                .call(spl_yAxis)
                .append("text")
                    //.attr("transform", "rotate(-90)")
                    .attr("y", 0)
                    .attr("dy", ".71em")
                    .style("text-anchor", "end");

            var metric_line = svg_left.selectAll(".metric_data")
                .data(metric_data)
                .enter().append("g")
                .attr("class", "metric_line");

            metric_line.append("path")
                .attr("class", "line")
                .attr("d", spl_line(metric_data))
                .style("stroke", "blue");

            svg_left.selectAll(".dot")
                .data(metric_data)
                .enter()
                .append("circle")
                .attr("class","dot")
                .attr("r", 4)
                .attr("cx", function(d) { return spl_xScale(d.year); })
                .attr("cy", function(d) { return spl_yScale(d.metric_value); })
                .on('mouseover',    lineTip.show)
                .on('mouseout',     lineTip.hide);
        }
    }


    function subRight() {
        /*
        Function to create the right subplot
        */

        // Ditch the subplot if it exists and redraw
        svg_right.selectAll(".subplot_right").remove();

        header = d3.select("#subplot_right")

        chart_title = "Demographic Features"

        // If a county has been selected...
        if(ctyID) {
            //sub_title = ctyLabel + " ("+yrLabel+")"
            drawBarChart()

        }
        else {
            header.select("h4").text(chart_title)
        }

    }

    function drawBarChart(group) {
        /*
        Function to draw the bar chart
        */

        svg_right.selectAll(".subplot_right").remove();

        // Grab the data for the county
        var filtered_raw_data = demoData.filter(function(d) {
            return d.id == ctyID;
        })
        //console.log(filtered_raw_data)

        //var group = 'age'

        // Get demo group info
        currentDemo = demo_hierarchy[demoVal];

        var group_cols      = currentDemo['fields'];
        var group_label     = currentDemo['label']
        var group_measure   = currentDemo['measure']
        //console.log("demo:",group_label,group_measure, group_cols)

        // Update the chart title
        demoDiv = d3.select("#subplot_right")
        demoDiv.select("h4").text(group_label)


        var metric_data = [];

        years.map(function(colYear) {

            rowDict = {}
            rowDict['id'] = ctyID;
            rowDict['year'] = colYear;

            group_cols.map(function(colName) {
                mcol = colName+"_"+colYear;
                //console.log(mcol, filtered_raw_data[0][mcol])
                rowDict[colName] = filtered_raw_data[0][mcol];
            })

            metric_data.push(rowDict)
            //console.log(rowDict)
        })

        //console.log(metric_data);

        spr_x0.domain(metric_data.map(function(d) { return d.year; }));
        spr_x1.domain(group_cols).rangeRound([0, spr_x0.bandwidth()]);
        spr_y.domain([0, d3.max(metric_data, function(d) { return d3.max(group_cols, function(key) { return d[key]; }); })]).nice();

        // Set different color ranges based on the number of columns
        if(group_cols.length==1){
            spr_z.range(["#0571b0"]);
        }
        else if(group_cols.length==2){
            spr_z.range(["#fc7303","#0571b0"])
        }
        else {
            spr_z.range(["#fc7303","#ffad5c","#f7f7f7","#92c5de","#0571b0"])
        }

        g = svg_right
            .append("g")
            .attr("transform", "translate(" + spr_margin.left + "," + spr_margin.top + ")")
            .attr("class", "subplot_right");

        g.append("g")
            .selectAll("g")
            .data(metric_data)
            .enter().append("g")
            .attr("class","bar")
            .attr("transform", function(d) { return "translate(" + spr_x0(d.year) + ",0)"; })
            .selectAll("rect")
            .data(function(d) { return group_cols.map(function(key) { return {key: key, value: d[key]}; }); })
            .enter().append("rect")
            .attr("x", function(d) { return spr_x1(d.key); })
            .attr("y", function(d) { return spr_y(d.value); })
            .attr("width", spr_x1.bandwidth())
            .attr("height", function(d) { return spr_height - spr_y(d.value); })
            .attr("fill", function(d) { return spr_z(d.key); });

        g.append("g")
            .attr("class", "spr_axis")
            .attr("transform", "translate(0," + spr_height + ")")
            .call(d3.axisBottom(spr_x0));

        g.append("g")
            .attr("class", "spr_axis")
            .call(d3.axisLeft(spr_y).ticks(null, "s"))
            .append("text")
            .attr("x", 2)
            .attr("y", spr_y(spr_y.ticks().pop()) - 10)
            .attr("dy", "0.32em")
            .attr("fill", "#000")
            .attr("font-weight", "bold")
            .attr("text-anchor", "start")
            .text(group_measure);


        // Draw the bar chart legend
        svgBarLegend.selectAll(".legend").remove();

        //-
        svgBarLegend
            .append("g")
            .attr("class", ".legend")

        var legend = svgBarLegend.selectAll(".legend")
            .data(group_cols.slice())
            .enter()
            .append("g")
            .attr("class", "legend")
            .attr("font-family", "sans-serif")
            .attr("font-size", 10)
            .attr("text-anchor", "start")
            .attr("transform", function(d, i) { return "translate(0," + i * 20 + ")"; });

        legend.append("rect")
            .attr("x", 10) //spr_width - 17)
            .attr("width", 15)
            .attr("height", 15)
            .attr("fill", spr_z)
            .attr("stroke", spr_z)
            .attr("stroke-width",2);
            //.on("click",function(d) { update(d) });

        legend.append("text")
            .attr("x", bar_legend_width-120)
            .attr("y", 9.5)
            .attr("dy", "0.32em")
            .text(function(d) { return demo_labels[d]; });

    }
}
