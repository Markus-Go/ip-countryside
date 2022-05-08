// global variable
let MAP;
let ip;

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

function syntaxHighlight(json) {
    if (typeof json != 'string') {
        json = JSON.stringify(json, undefined, 2);
    }
    json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
        var cls = 'text-success';
        if (/^"/.test(match)) {
            if (/:$/.test(match)) {
                cls = 'text-primary';
            } else {
                cls = 'text-info';
            }
        } else if (/true|false/.test(match)) {
            cls = 'text-danger';
        } else if (/null/.test(match)) {
            cls = 'text-secondary';
        }
        return '<span class="' + cls + '">' + match + '</span>';
        })
}