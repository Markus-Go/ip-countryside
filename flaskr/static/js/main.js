// global variable
let MAP;

function init_map(map, lat, lon, ip) {
    
    if(map == null)
        map = L.map('map').fitWorld();

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    L.marker([lat, lon]).addTo(map)
    .bindPopup(ip)
    .openPopup();

}