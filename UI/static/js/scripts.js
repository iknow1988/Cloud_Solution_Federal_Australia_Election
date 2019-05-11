
(function() {
	
  var map = L.map('map', {
    attributionControl: false
  });
    var state_twitter;
	var arr2 = [['state','Percentage of tweets', 'Percentage of votes']]
	fetch('http://127.0.0.1:5000/state/')
	.then(response => {
		return response.json()
	})
    .then(data => {
		state_twitter = data;
	})
	
	var state_party;
	fetch('http://127.0.0.1:5000/scenario_1_2/')
	.then(response => {
		return response.json()
	})
    .then(data => {
		state_party = data;
	})
  
  
  L.tileLayer('http://{s}.tile.stamen.com/{style}/{z}/{x}/{y}.png', { style: 'toner-background' }).addTo(map);
  
  $.getJSON("static/js/states.geojson", function(data) {

    var info = L.control();
    info.update = function (props) {
		if(props){
			var state_total_tweets = state_twitter[parseInt(props['STATE_CODE'])];
			var state_party_vote = state_party[parseInt(props['STATE_CODE'])];

			arr2 = [];
			arr2.push(['state','Percentage of tweets', 'Percentage of votes']);
			for (var i in state_party_vote){
				arr2.push([i,state_party_vote[i][0]*100, state_party_vote[i][1]*100])
			}
			this._div.innerHTML = '<b>' + props['STATE_NAME'] + '</b>' ;
			this._div.innerHTML += '<br><br><b> Number of Tweets : </b>' + state_total_tweets;
			google.charts.load("current",  {packages: ["corechart"]});
			google.charts.setOnLoadCallback(drawBarChart);
			function drawBarChart() {
				

				var data1 = google.visualization.arrayToDataTable(arr2);
				var view1 = new google.visualization.DataView(data1);
  

				var options1 = {'title': "DING DONG", 'width':550, 'height':400, 
					legend: { position: 'top', maxLines: 3 },
					theme: 'material',
					tooltip: { isHtml: true},
					backgroundColor: { fill:'transparent' },
					animation: {
						duration: 300,
						startup: true
				}};
				
				var chart1 = new google.visualization.ColumnChart(document.getElementById('map2'));
				chart1.draw(view1, options1);
			}
			
		}else{
			this._div.innerHTML = '<b> Hover over a state </b>';
			//document.getElementById("map2").innerHTML = "";
		}
		
    };
	
    info.onAdd = function (map) {
      this._div = L.DomUtil.create('div', 'info'); // create a div with a class "info"
      this.update();
      return this._div;
    };

    info.addTo(map);

    var geojson = L.geoJson(data, {
      style: function (feature) {
        return {
          color: '#3498db',
          weight: 2,
          fillOpacity: 0.5
        };
      },
      onEachFeature: function (feature, layer) {
        // layer.bindPopup(feature.properties['STATE_NAME']);

        layer
        .on('mouseover', function(e) {
          layer.setStyle({
            weight: 4,
            fillOpacity: 0.8
          });
          info.update(layer.feature.properties);
        })
        .on('mouseout', function(e) {
          geojson.resetStyle(layer);
          info.update();
        })
		.on('click', function(e) {
			map.fitBounds(layer);
        })
      }
    })
	
	

    geojson.addTo(map);
    var bounds = geojson.getBounds();
    map.fitBounds(bounds);

    map.options.maxBounds = bounds;
    map.options.minZoom = map.getZoom();
  });

})();
