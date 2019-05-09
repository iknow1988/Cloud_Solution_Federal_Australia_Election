
var total_count;
var arr = [['state','Number of tweets']];
fetch('http://127.0.0.1:5000/initial/')
.then(response => {
    return response.json()
})
.then(data => {
    // Work with JSON data here
	var count = 0;
	for (var i in data){
		count += data[i];
		arr.push([i,data[i]])
	}
	total_count  = 	'Total Numer of Tweets ' + count
	// Load google charts
	//google.charts.load('43', {'packages':['corechart']});
	google.load("visualization", "1.1", {
        packages: ["corechart"]
    });
	google.setOnLoadCallback(drawChart);
})
  



// Draw the chart and set the chart values
function drawChart() {
   

  var data = google.visualization.arrayToDataTable(arr);

  // Optional; add a title and set the width and height of the chart

  var options = {'title': total_count, 'width':550, 'height':400, animation: {
                duration: 1500,
                startup: true
            }};
  // Display the chart inside the <div> element with id="piechart"
  var chart = new google.visualization.PieChart(document.getElementById('map1'));
  chart.draw(data, options);
}