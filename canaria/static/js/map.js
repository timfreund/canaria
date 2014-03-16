var svg = null;
var height = $(window).height() - 300;
var width = $(window).width() - 50;

var projection = d3.geo.albersUsa().scale(850).translate([width / 2, height / 2]);
var path = d3.geo.path().projection(projection);
var color = d3.scale.log()
  .range([0, 255]);

var data = null;
var features = null;

function drawMap(){
    svg = d3.select("svg");
    if(svg[0][0] == null){
        svg = d3.select("body")
            .append("svg")
            .attr("width", width)
            .attr("height", height);
    }

    d3.json("/api/v1/coalproduction/2011/us/?group=state", function(error, production){
        data = production.data;
        color.domain([d3.min(data, function(d) { return d.production;}),
                      d3.max(data, function(d) { return d.production;})]);

        d3.json("/static/apidemo/us_states-topo.json", function(error, us){
            for(var x = 0; x < data.length; x++) {
                var datum = data[x];
                console.log(us.objects.us_states.geometries.length);
                for(var y = 0; y < us.objects.us_states.geometries.length; y++){
                    var geometry = us.objects.us_states.geometries[y];
                    if(geometry.properties.STATE == datum.state){
                        geometry.properties.production = datum.production;
                        geometry.properties.average_employees = datum.average_employees;
                        geometry.properties.labor_hours = datum.labor_hours;
                        break;
                    }
                }
            }

            features = [];
            for (var x = 0; x < us.objects.us_states.geometries.length; x++){
                //console.log(x);
                features[x] = topojson.feature(us, us.objects.us_states.geometries[x]);
            }

            svg.selectAll("path")
            .data(features)
            .enter()
            .append("path")
            .attr("d", path)
            .attr("class", function(d){ d.properties.STATE})
            .style("stroke", "#222")
                .style("fill", function(d){
                    var value = d.properties.production;
                    if(value){
                        return "rgb(0, 0, " + Math.floor(color(value)) + ")";
                    } else {
                        return "#eee";
                    }
                });
        });
    });
}

function renderData(dataKey){
    color.domain([d3.min(features, function(d) {return d.properties[dataKey];}),
                  d3.max(features, function(d) {return d.properties[dataKey];})]);
    svg.selectAll("path")
      .data(features)
      .style("fill", function(d){
          var value = d.properties[dataKey];
          if(value){
              return "rgb(0, 0, " + Math.floor(color(value)) + ")";
          } else {
              return "#eee";
          }
      });
}

function executeMapDemo(){
    drawMap();
}

