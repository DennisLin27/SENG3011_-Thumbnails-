// This example requires the Places library. Include the libraries=places
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">
function initMap() {

    map = new google.maps.Map(document.getElementById("map"), {
        center: {lat:-33.867, lng:151.195},
        zoom: 13.5,
        mapTypeControl: false,
    });

    const input = document.getElementById("pac-input");
    const options = {
        fields: ["formatted_address", "geometry", "name"],
        types: ["address"],
    };

    const autocomplete = new google.maps.places.Autocomplete(input, options);
    const infowindow = new google.maps.InfoWindow();
    const infowindowContent = document.getElementById("infowindow-content");
    infowindow.setContent(infowindowContent);

    const marker = new google.maps.Marker({
        map,
        anchorPoint: new google.maps.Point(0, -29),
    });

    autocomplete.addListener("place_changed", () => {
        infowindow.close();
        //marker.setVisible(false);

        const place = autocomplete.getPlace();

        if (!place.geometry || !place.geometry.location) {
        // User entered the name of a Place that was not suggested and
        // pressed the Enter key, or the Place Details request failed.
        window.alert("No details available for input: '" + place.name + "'");
        return;
        }

        // If the place has a geometry, then present it on a map.
        if (place.geometry.viewport) {
        map.fitBounds(place.geometry.viewport);
        } else {
        map.setCenter(place.geometry.location);
        map.setZoom(13);
        }

        //marker.setPosition(place.geometry.location);
        //marker.setVisible(true);
        infowindowContent.children["place-name"].textContent = place.name;
        infowindowContent.children["place-address"].textContent =
        place.formatted_address;
        infowindow.open(map, marker);

        createAnchor(place)
        searchNearby(place)
        map.setZoom(13)
    });

}

function searchNearby(place) {
    var request = {
        location: place.geometry.location,
        radius: '2000',
        type: ['pharmacy']
    };

    service = new google.maps.places. PlacesService(map);
    service.nearbySearch(request, callback);
}

function callback(results, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
            console.log(results[i])
            createMarker(results[i]);
        }
    }
  }

function createMarker(place){
    if (!place.geometry || !place.geometry.location) return;

    new google.maps.Marker({
        position: place.geometry.location,
        map
      });
}

function createAnchor(place){
    if (!place.geometry || !place.geometry.location) return;

    new google.maps.Marker({
        position: place.geometry.location,
        animation: google.maps.Animation.BOUNCE,

        map: map
      });
}