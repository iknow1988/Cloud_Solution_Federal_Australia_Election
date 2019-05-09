
(function() {
	
  var map = L.map('map', {
    attributionControl: false
  });
    var state_twitter;
	
	fetch('http://127.0.0.1:5000/state/')
	.then(response => {
		return response.json()
	})
    .then(data => {
		state_twitter = data;
	})
  
  
  L.tileLayer('http://{s}.tile.stamen.com/{style}/{z}/{x}/{y}.png', { style: 'toner-background' }).addTo(map);
  
  $.getJSON("states.geojson", function(data) {

    var info = L.control();
    info.update = function (props) {
		if(props){
			var state_total_tweets = state_twitter[parseInt(props['STATE_CODE'])];
			this._div.innerHTML = '<b>' + props['STATE_NAME'] + '</b>' ;
			this._div.innerHTML += '<br><br><b> Number of Tweets : </b>' + state_total_tweets;
		}else{
			this._div.innerHTML = '<b> Hover over a state </b>';
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
      }
    })

    geojson.addTo(map);
    var bounds = geojson.getBounds();

    map.fitBounds(bounds);

    map.options.maxBounds = bounds;
    map.options.minZoom = map.getZoom();
  });

})();
