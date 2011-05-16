function showMap() {
    //initialize map
    var map = new YMaps.Map($('#YMapsID'));
    map.enableScrollZoom();
    map.enableRightButtonMagnifier();

    default_address = new YMaps.Geocoder('г. Владивосток', { results: 1 });
    YMaps.Events.observe(default_address, default_address.Events.Load, function(default_address) {
        map.setCenter(default_address.get(0).getBounds().getCenter(), 8);
    });
    var list = $('<ol>');
    
    function addPlacemark(a, name, value, style) {
        var i = new YMaps.Placemark(a.get(0).getGeoPoint(), { style: style });
        i.name = name;
        i.description = value;
        map.addOverlay(i);
        
        var li = $('<li>');
        li
            .html(i.name + ': ' + i.description)
            .click({ point: i }, function(eventObject) {
                map.setCenter(eventObject.data.point.getGeoPoint(), 8);
            })
            .appendTo(list);
    }
    
    $.get(
        '/theMarket/map_data/', {},
        function(data) {
            var addressCount = 0;
            $.each(
                data,
                function(index, value) {
                    if(value == '')
                        return;
                        
                    var address = new YMaps.Geocoder(value, { results: 1 });
                    
                    YMaps.Events.observe(address, address.Events.Load, function(address) {
                        if(address.length()) {
                            addressCount++;
                            if(index == 0)
                                addPlacemark(address, 'Your location', value, 'default#houseIcon');
                            else
                                addPlacemark(address, 'Office', value, 'default#shopIcon');
                            if(addressCount == 1 || index == 0)
                                map.setCenter(address.get(0).getBounds().getCenter(), 8);
                        }
                    });
                }
            );
        }
    );
    $('#office_addresses').html('').append(list);
}

$(document).ready(function () {
    showMap();
});