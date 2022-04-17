// This example requires the Places library. Include the libraries=places
// parameter when you first load the API. For example:
// <script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places">

var marker_list = new Array

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
        radius: 3000
    };

    const autocomplete = new google.maps.places.Autocomplete(input, options);

    const marker = new google.maps.Marker({
        map,
        anchorPoint: new google.maps.Point(0, -29),
    });

    autocomplete.addListener("place_changed", () => {

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

        place.formatted_address;
        searchNearby(place)
        createAnchor(place)
        map.setZoom(13)
    });

}

function searchNearby(place) {

    var request = {
        location: place.geometry.location,
        radius: 3000,
        type: ['doctor']
    };

    service = new google.maps.places. PlacesService(map);
    removeMarkers()
    service.nearbySearch(request, callback);
}

function removeMarkers(){
    for (var i = 0; i < marker_list.length; i++){
        marker_list[i].setMap(null)
    }
    marker_list = []

    for (var x = 0; x < anchorList.length; x++){
        anchorList[x].setMap(null)
    }
    anchorList = []
}

function callback(results, status) {
    if (status == google.maps.places.PlacesServiceStatus.OK) {
        for (var i = 0; i < results.length; i++) {
            console.log(results[i])
            //createMarker(results[i]);
            
            const marker = new google.maps.Marker({
                position: results[i].geometry.location,
                map,
                optimized: false,
            });

            const contentString = 
                '<div id = "content">' + 
                '<p><b>Name: </b>' + results[i].name + 
                '</p><p><b>Address: </b>' + results[i].vicinity + '</p>' +
                '</div>'       

            const infoWindow = new google.maps.InfoWindow({
                content: contentString
            })


            marker.addListener("click",() => {
                infoWindow.open({
                    anchor:marker,
                    map,
                })
            })

            marker_list.push(marker)
        }
    }
  }

var anchorList = new Array
function createAnchor(place){
    if (!place.geometry || !place.geometry.location) return;

    anchor = new google.maps.Marker({
        position: place.geometry.location,
        map: map,
        title: "Your Location",
        icon: {
            url: 'home-map-location.png',
            scaledSize: new google.maps.Size(25,25)
        },
      });
    anchorList.push(anchor)
}