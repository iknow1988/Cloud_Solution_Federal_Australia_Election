
var total_count;
var arr = [['state','Number of tweets']];
var arr1 = [['state','Percentage of tweets', 'Percentage of votes']]
fetch('http://127.0.0.1:5000/scenario_1_1/')
.then(response => {
    return response.json()
})
.then(data => {
    // Work with JSON data here
	for (var i in data){
		arr1.push([i,data[i][0]*100, data[i][1]*100])
	}
	google.charts.load("current",  {packages: ["corechart"]});
	google.charts.setOnLoadCallback(drawChart);

	
})

fetch('http://127.0.0.1:5000/initial/')
.then(response => {
    return response.json()
})
.then(data => {
    // Work with JSON data here
	var count = 0;
	for (var i in data){
		count += data[i];
		arr.push([i,data[i]]);
	}
	total_count  = 	'Total Numer of Tweets ' + count;
	// Load google charts
	//google.charts.load('43', {'packages':['corechart']});
	
})
  



// Draw the chart and set the chart values
function drawChart() {
   

  var data = google.visualization.arrayToDataTable(arr1);
  var view = new google.visualization.DataView(data);
  // Optional; add a title and set the width and height of the chart

  var options = {'title': "DING DONG", 'width':550, 'height':400, 
			legend: { position: 'top', maxLines: 3 },
			theme: 'material',
			tooltip: { isHtml: true},
			backgroundColor: { fill:'transparent' },
			animation: {
                duration: 1500,
                startup: true
            }};
  // Display the chart inside the <div> element with id="piechart"
  
  var chart = new google.visualization.ColumnChart(document.getElementById('map1'));
  chart.draw(view, options);
}