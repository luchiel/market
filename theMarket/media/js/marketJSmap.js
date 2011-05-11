function showMap() {
    //initialize map
    var map = new YMaps.Map($('#YMapsID'));
    map.enableScrollZoom();
    map.enableRightButtonMagnifier();

    function addPlacemark(a, name, value, style) {
        var i = new YMaps.Placemark(a.get(0).getGeoPoint(), { style: style });
        i.name = name;
        i.description = value;
        map.addOverlay(i);
    }
    
    //get addresses
    $.get(
        '/theMarket/map_data/', {},
        function(data) {
            //process addresses
            $.each(
                data,
                function(index, value) {
                    if(value == '' && index == 0)
                        value = 'г. Владивосток';
                    else if(value == '')
                        return;
                    var address = new YMaps.Geocoder(value, { results: 1 });
                    
                    YMaps.Events.observe(address, address.Events.Load, function(address) {
                        if(index == 0) {
                            if(address.length()) {
                                addPlacemark(address, 'Your location', value, 'default#houseIcon');
                                map.setCenter(address.get(0).getBounds().getCenter(), 8);
                            }
                            else {
                                default_address = new YMaps.Geocoder('г. Владивосток', { results: 1 });
                                YMaps.Events.observe(default_address, default_address.Events.Load, function(default_address) {
                                    addPlacemark(default_address, 'Your location', value, 'default#houseIcon');
                                    map.setCenter(default_address.get(0).getBounds().getCenter(), 8);
                                });
                            }
                        }
                        else {
                            if(address.length())
                                addPlacemark(address, 'Office', value, 'default#shopIcon');
                        }
                    });
                }
            );
        }
    );
}

$(document).ready(function () {
    showMap();
});