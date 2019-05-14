
(function() {
	
  var map = L.map('map', {
    attributionControl: false
  });
    var state_twitter;
	var state_name;
	var arr2 = [['state','Percentage of tweets', 'Percentage of votes']]
	fetch('http://127.0.0.1:80/state/')
	.then(response => {
		return response.json()
	})
    .then(data => {
		state_twitter = data;
	})
	
	var state_party;
	fetch('http://127.0.0.1:80/scenario_1_2/')
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
			state_name = props['STATE_NAME'];
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
				
		
					if(i == 0){
						title3 = "Australian Greens";
						placeholder = "pie3";
						
						var options3 = {'title': title3, 'width':250, 'height':250, 
						legend: { position: 'top', maxLines: 3 },
						theme: 'material',
						tooltip: { isHtml: true},
						backgroundColor: { fill:'transparent' },
						animation: {
							duration: 1500,
							startup: true
						}};
						var data3 = google.visualization.arrayToDataTable(pol_arr[i]);
						var view3 = new google.visualization.DataView(data3);
						var chart3 = new google.visualization.PieChart(document.getElementById(placeholder));
						google.visualization.events.addListener(chart3, 'select', selectHandler3);
					
						chart3.draw(view3, options3);
					}else if (i == 1){
						title2 = "Australian Labor Party";
						placeholder = "pie2";
						
						var options2 = {'title': title2, 'width':250, 'height':250, 
						legend: { position: 'top', maxLines: 3 },
						theme: 'material',
						tooltip: { isHtml: true},
						backgroundColor: { fill:'transparent' },
						animation: {
							duration: 1500,
							startup: true
						}};
						var data2 = google.visualization.arrayToDataTable(pol_arr[i]);
						var view2 = new google.visualization.DataView(data2);
						var chart2 = new google.visualization.PieChart(document.getElementById(placeholder));
						google.visualization.events.addListener(chart2, 'select', selectHandler2);
					
						chart2.draw(view2, options2);
					}
					else if (i == 2){
						title1 = "Liberal Party";
						placeholder = "pie1";
						
						var options1 = {'title': title1, 'width':250, 'height':250, 
						legend: { position: 'top', maxLines: 3 },
						theme: 'material',
						tooltip: { isHtml: true},
						backgroundColor: { fill:'transparent' },
						animation: {
							duration: 1500,
							startup: true
						}};
						var data1 = google.visualization.arrayToDataTable(pol_arr[i]);
						var view1 = new google.visualization.DataView(data1);
						var chart1 = new google.visualization.PieChart(document.getElementById(placeholder));
						google.visualization.events.addListener(chart1, 'select', selectHandler1);
					
						chart1.draw(view1, options1);
					}
					else if (i == 3){
						title4 = "United Australia Party";
						placeholder = "pie4";
						
						var options4 = {'title': title4, 'width':250, 'height':250, 
						legend: { position: 'top', maxLines: 3 },
						theme: 'material',
						tooltip: { isHtml: true},
						backgroundColor: { fill:'transparent' },
						animation: {
							duration: 1500,
							startup: true
						}};
						var data4 = google.visualization.arrayToDataTable(pol_arr[i]);
						var view4 = new google.visualization.DataView(data3);
						var chart4 = new google.visualization.PieChart(document.getElementById(placeholder));
						google.visualization.events.addListener(chart4, 'select', selectHandler4);
					
						chart4.draw(view4, options4);
					}

					
					
					function selectHandler1(){
						console.log(state_name)
						console.log(title1)
						var selectedItem = chart1.getSelection()[0];
						var value = selectedItem.row;
						if (value == "1" || value == "0"){
				
							var str = 'http://127.0.0.1:80/gettopwords/?state='+state_name+'&party='+title1+'&poll='+value
							fetch(str)
								.then(response => {
									return response.json()
							})
							.then(data => {
								console.log(data)
							})
							
							
						}
							

					}
					function selectHandler2(){
						console.log(state_name);
						console.log(title2);
						var selectedItem = chart2.getSelection()[0];
						var value = selectedItem.row;
							
					}
					function selectHandler3(){
						console.log(state_name)
						console.log(title3)
						var selectedItem = chart3.getSelection()[0];
						var value = selectedItem.row;
					}
					function selectHandler4(){
						console.log(state_name)
						console.log(title4)
						var selectedItem = chart4.getSelection()[0];
						var value = selectedItem.row;
					}
					
				
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
