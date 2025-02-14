document.addEventListener("DOMContentLoaded", function () {
    var map = L.map("map").setView([51.1657, 10.4515], 6);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    var heatmapLayer = L.heatLayer([], {
        radius: 25,
        blur: 15,
        maxZoom: 17,
        minOpacity: 0.5,
        gradient: {
            0.2: "#0000FF",
            0.4: "#00FFFF",
            0.6: "#00FF00",
            0.8: "#FFFF00",
            1.0: "#FF0000"
        }
    }).addTo(map);

    var eventMarkers = L.layerGroup().addTo(map);

    fetch("/api/heatmap")
        .then(response => response.json())
        .then(data => {
            console.log("API-Daten:", data);
            var heatPoints = [];

            data.heatmap.forEach(event => {
                var lat = event.location.lat;
                var lon = event.location.lon;
                var popupContent = `
                    <b>${event.location.name}</b><br>
                    ${event.timestamp}<br>
                    <i>${event.source}</i><br>
                    <p>${event.summary || "Keine Beschreibung verfügbar"}</p>
                `;

                heatPoints.push([lat, lon, event.threat_level || 0.5]);

                var circleMarker = L.circleMarker([lat, lon], {
                    color: "#00CED1",
                    fillColor: "#00CED1",
                    fillOpacity: 0.9,
                    radius: 5,
                    weight: 0
                }).bindPopup(popupContent);

                eventMarkers.addLayer(circleMarker);
            });

            heatmapLayer.setLatLngs(heatPoints);
        })
        .catch(error => console.error("Fehler beim Laden der Heatmap-Daten:", error));
});