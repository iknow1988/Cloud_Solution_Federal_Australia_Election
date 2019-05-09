

fetch('http://127.0.0.1:5000/')
  .then(response => {
    return response.json()
  })
  .then(data => {
    // Work with JSON data here
	document.getElementById('map1').innerHTML += '<br> <br> <br> Total Tweet Count : ' + data.count;
  })
  .catch(err => {
	  console.log("hello")
    // Do something for an error here
  })