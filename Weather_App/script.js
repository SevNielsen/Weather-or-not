
function fetchWeatherData(lat, lon) {
    fetch('/get_weather', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({lat: lat, lon: lon})
    })
    .then(response => response.json())
    .then(data => {
        // Process and display the weather data received from your Flask backend
        console.log(data); // For debugging
        // Update your UI with this data
    })
    .catch(error => {
        console.error('Error fetching weather data:', error);
    });
}


var map = L.map('mapid').setView([your_initial_latitude, your_initial_longitude], 13);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

var marker;

map.on('click', function(e) {
    var lat = e.latlng.lat;
    var lon = e.latlng.lng;
    
    if (marker) {
        map.removeLayer(marker);
    }

    marker = L.marker([lat, lon]).addTo(map);

    // Use lat and lon to fetch weather data from OpenWeatherMap API
    fetchWeatherData(lat, lon);
});

function fetchWeatherData(lat, lon) {
    // Your code to call the OpenWeatherMap API and display the weather data
}
