function initMap() {

    infowindow = new google.maps.InfoWindow();

    map = new google.maps.Map(document.getElementById('map'), {
        center: {lat:-33.867, lng:151.195}, 
        zoom: 15
    });


    var request = {
        location: sydney,
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

    var marker = new google.maps.Marker({
        position: place.geometry.location,
        map
      });
}
