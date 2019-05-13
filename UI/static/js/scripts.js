
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
  
  
  L.tileLayer('https://api.maptiler.com/maps/basic/{z}/{x}/{y}.png?key=8SXGwerAtAzQSi65BPF0', { attribution: '<a href="https://www.maptiler.com/copyright/" target="_blank">© MapTiler</a> <a href="https://www.openstreetmap.org/copyright" target="_blank">© OpenStreetMap contributors</a>' }).addTo(map);
  
  $.getJSON("static/js/states.geojson", function(data) {

    var info = L.control();
    info.update = function (props) {
		if(props){
			var state_total_tweets = state_twitter[parseInt(props['STATE_CODE'])];
			var state_party_vote = state_party[parseInt(props['STATE_CODE'])];

			arr2 = [];
			arr2.push(['state','Percentage of tweets', 'Percentage of votes']);
			var pol_arr = new Array(4);

			for (var i = 0; i < pol_arr.length; i++) {
				pol_arr[i] = [];
				pol_arr[i].push(['Polarity', 'Percentage']);
			}
			x = 0;
			for (var i in state_party_vote){
				arr2.push([i,state_party_vote[i][0]*100, state_party_vote[i][1]*100])
				pol_arr[x].push(['Positive', state_party_vote[i][2]*100 ]);
				pol_arr[x].push(['Negative', state_party_vote[i][3]*100 ]);
				pol_arr[x].push(['Neutral', state_party_vote[i][4]*100 ]);
				x = x + 1;
			}
			
			for (var i = 0; i < pol_arr.length; i++) {
				console.log(pol_arr[i]);
			}
			this._div.innerHTML = '<b>' + props['STATE_NAME'] + '</b>' ;
			this._div.innerHTML += '<b> &nbsp; &nbsp; Number of Tweets : </b>' + state_total_tweets;
			google.charts.load("current",  {packages: ["corechart"]});
			google.charts.setOnLoadCallback(drawBarChart);
			function drawBarChart() {
				

				var data1 = google.visualization.arrayToDataTable(arr2);
				var view1 = new google.visualization.DataView(data1);
  

				var options1 = {'title': "", 'width':550, 'height':300, 
					legend: { position: 'bottom', maxLines: 3 },
					theme: 'material',
					tooltip: { isHtml: true},
					backgroundColor: { fill:'transparent' },
					animation: {
						duration: 300,
						startup: true
				}};
				
				var chart1 = new google.visualization.ColumnChart(document.getElementById('map2'));
				chart1.draw(view1, options1);
				
				for (var i = 0; i < pol_arr.length; i++) {
				
					var data1 = google.visualization.arrayToDataTable(pol_arr[i]);
					var view1 = new google.visualization.DataView(data1);
					if(i == 0){
						title = "Australian Greens";
						placeholder = "pie3";
					}else if (i == 1){
						title = "Australian Labor Party";
						placeholder = "pie2";
					}
					else if (i == 2){
						title = "Liberal Party";
						placeholder = "pie1";
					}
					else if (i == 3){
						title = "United Australia Party";
						placeholder = "pie4";
					}

					var options1 = {'title': title, 'width':250, 'height':250, 
						legend: { position: 'top', maxLines: 3 },
						theme: 'material',
						tooltip: { isHtml: true},
						backgroundColor: { fill:'transparent' },
						animation: {
							duration: 1500,
							startup: true
					}};
				
					var chart1 = new google.visualization.PieChart(document.getElementById(placeholder));
					chart1.draw(view1, options1);
				
				
				}
				
				
			}
			
		}else{
			//this._div.innerHTML = '<b> Hover over a state </b>';
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
          weight: 1,
          fillOpacity: 0.1
        };
      },
      onEachFeature: function (feature, layer) {
        // layer.bindPopup(feature.properties['STATE_NAME']);

        layer
        .on('mouseover', function(e) {
          layer.setStyle({
            weight: 2,
            fillOpacity: 0.3
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
