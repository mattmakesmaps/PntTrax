/**
 * Created with PyCharm.
 * User: matt
 * Date: 12/18/12
 * Time: 9:37 PM
 * To change this template use File | Settings | File Templates.
 * 47.6097° N, 122.3331° W
 */
var geoJsonBaseURL = "../../../gpstracker/geojson/";

var pointGroupURL = geoJsonBaseURL + "point/group/" + group_id + "/";
var lineGroupURL = geoJsonBaseURL + "line/group/" + group_id + "/";
var polyGroupURL = geoJsonBaseURL + "poly/group/" + group_id + "/";

var map = L.map('map').setView([0, 0], 1);

var cloudmadeUrl = 'http://{s}.tile.cloudmade.com/5df4a1ed4a8c41bd91725ad594aa6139/997/256/{z}/{x}/{y}.png';
var cloudmadeAttrib = 'Map data &copy; 2011 OSM contributors, Style &copy; 2011 CloudMade';
var cloudmade = new L.TileLayer(cloudmadeUrl, {
    maxZoom: 18,
    attribution: cloudmadeAttrib
});

var mapQuestAerialURL = 'http://{s}.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.png';
var mapQuestAerialAttrib = 'Portions Courtesy NASA/JPL-CalTech, USDA FSA. Thanks MapQuest!';
var mapQuestAerial = new L.TileLayer(mapQuestAerialURL, {
    attribution: mapQuestAerialAttrib,
    subdomains: ['oatile1', 'oatile2', 'oatile3', 'oatile4']
});
map.addLayer(mapQuestAerial);

var bing = new L.BingLayer("AioA0H5rhfSjb4azjZSw7T66OVeoHnq_CIUAF-kZS-PW8bkULkdqRlKTDFzbZ5gk");
map.addLayer(bing);

function onEachFeature(feature, layer) {
    // autoPanPadding value of 50 px is good for retina display
    // how does this look on a non-retina display?
    if (feature.properties && feature.properties.name && feature.properties.comment && feature.properties.featurePurpose && feature.properties.collectionMethod) {
        layer.bindPopup("<b>" + feature.properties.name + "</b></br>" + "<b>Feature Purpose: </b>" + feature.properties.featurePurpose + "</br>" + "<b>Collection Method: </b>" + feature.properties.collectionMethod + "</br>" + "<b>Comment: </b>" + feature.properties.comment, { autoPan: true, autoPanPadding: new L.Point(50, 50)});
    } else if (feature.properties && feature.properties.name ) {
        layer.bindPopup("<b>" + feature.properties.name + "</b>", { autoPan: true, autoPanPadding: new L.Point(50, 50)});
    }

}

// Set Icon Based On Feature Purpose Attribute
function makeIcon(feature) {
    switch (feature.properties.featurePurpose) {
        case 'Monitoring Well': myIconUrl = "../../../static/img/monitoring_well_32.png"; break;
        case 'Sampling Location': myIconUrl = "../../../static/img/sampling_location_36.png"; break;
        case 'Site Feature': myIconUrl = "../../../static/img/feature_36.png"; break;
        case 'Unknown': myIconUrl = "../../../static/img/unknown_36.png"; break;
        case 'Photo Point': myIconUrl = "../../../static/img/camera_36.png"; break;
        default: myIconUrl = "../../../static/img/feature_36.png";
    };

    var typeIcon = L.icon({
    iconUrl: myIconUrl,
    iconSize: [28,28],
    iconAnchor: [0,0],
    popupAnchor: [13,13]
});
    return typeIcon
}

var baseMaps = {"Roads (OSM)": cloudmade, "Aerial (Mapquest)": mapQuestAerial, "Aerial (Bing)": bing};
var pointGeoJSON = new L.GeoJSON('',{
    pointToLayer: function (feature, latlng) {
        return L.marker(latlng, {icon: makeIcon(feature)});
    },
    onEachFeature: onEachFeature
});
var lineGeoJSON = new L.GeoJSON('',{onEachFeature: onEachFeature});
var polyGeoJSON = new L.GeoJSON('',{onEachFeature: onEachFeature});
var layersControl = new L.Control.Layers(baseMaps);
map.addControl(layersControl);

function makePointLayer(data) {
    pointGeoJSON.addData(data);
    pointGeoJSON.addTo(map);
    // Zoom to bounds of point.
    map.fitBounds(pointGeoJSON.getBounds());
}

function makeLineLayer(data) {
    lineGeoJSON.addData(data);
    lineGeoJSON.addTo(map);
}

function makePolyLayer(data) {
    polyGeoJSON.addData(data);
    polyGeoJSON.addTo(map);
}

// Make call to GeoJSON Service
// Check to see if point/line/polys exist for the given group
if (point_success === true) $.getJSON(pointGroupURL, makePointLayer);
if (line_success === true) $.getJSON(lineGroupURL, makeLineLayer);
if (poly_success === true) $.getJSON(polyGroupURL, makePolyLayer);

// Add click event to table row.
$('.table > tbody > tr').click(function(event){
    switch ($(this).parents('table').attr('id')) {
        case 'point_table': var clickedLayer = pointGeoJSON; break;
        case 'line_table': var clickedLayer = lineGeoJSON; break;
        case 'poly_table': var clickedLayer = polyGeoJSON; break;
        default: var clickedLayer = false;
    };
    // loop through elements in pointGeoJSON object.
    for (var prop in clickedLayer._layers) {
        // if the id of the row matches the id of the map object, open the popup.
        if (clickedLayer._layers[prop].feature.id == this.id) {
//            console.log('point GeoJSON has id', clickedLayer._layers[prop].feature.id);
            clickedLayer._layers[prop].openPopup();
        };
    };
});
