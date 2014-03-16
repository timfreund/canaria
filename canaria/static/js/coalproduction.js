
var height = $(window).height() - 300;
var width = $(window).width() - 50;
var xScale = d3.scale.linear();
var yScale = d3.scale.linear();

var rawCoalData = null;
var coalData = null;

function fetchData(year, state, county, grouped){
    url = "/v1/coalproduction/" + year + "/us";
    if(state){
        url = url + "/" + state;
    }
    if(county){
        url = url + "/" + county;
    }
    if(grouped){
        url = url + "?group=" + grouped;
    }

    $.ajax({
        url: url,
        type: 'GET',
        dataType: 'json',
        success: function(incoming) { coalData = incoming; transformCoalProductionData(); },
    });
}

function transformCoalProductionData(){
    coalData = rawCoalData.production;

    xScale.domain([0, len(coalData)]);
    xScale.range([0, width]);
    yScale.domain([0, d3.max(coalData, function(d) { return d.production; } )]);
    yScale.range([0, height]);

    renderCoalProduction();
}

function renderCoalProduction(){
    var svg = d3.select("svg");
    if(svg[0][0] == null){
        svg = d3.select("body")
          .append("svg")
          .attr({"width": width,
                 "height": height});
    }
}
