/**
 * Created with PyCharm.
 * User: matt
 * Date: 12/18/12
 * Time: 9:37 PM
 * To change this template use File | Settings | File Templates.
 * 47.6097° N, 122.3331° W
 */
var geoJsonBaseURL = "http://127.0.0.1:8000/GPSTracker/geojson/";

var pointGroupURL = geoJsonBaseURL + "point/group/" + group_id + "/";
var lineGroupURL = geoJsonBaseURL + "line/group/" + group_id + "/";
var polyGroupURL = geoJsonBaseURL + "poly/group/" + group_id + "/";

var myStyle = {
    "color": "#ff7800",
    "weight": 5,
    "opacity": 0.65
};

var map = L.map('map').setView([0, 0], 1);

var cloudmadeUrl = 'http://{s}.tile.cloudmade.com/5df4a1ed4a8c41bd91725ad594aa6139/997/256/{z}/{x}/{y}.png';
var cloudmadeAttrib = 'Map data &copy; 2011 OSM contributors, Style &copy; 2011 CloudMade';
var cloudmade = new L.TileLayer(cloudmadeUrl, {maxZoom: 18, attribution: cloudmadeAttrib});

var mapQuestAerialURL = 'http://{s}.mqcdn.com/tiles/1.0.0/sat/{z}/{x}/{y}.png';
var mapQuestAerialAttrib = 'Portions Courtesy NASA/JPL-CalTech, USDA FSA. Thanks MapQuest!';
var mapQuestAerial = new L.TileLayer(mapQuestAerialURL, {
    maxZoom: 18,
    attribution: mapQuestAerialAttrib,
    subdomains: ['oatile1', 'oatile2', 'oatile3', 'oatile4']
});
map.addLayer(mapQuestAerial);

var baseMaps = {"Road": cloudmade, "Aerial": mapQuestAerial};
var pointGeoJSON = new L.GeoJSON();
var lineGeoJSON = new L.GeoJSON();
var polyGeoJSON = new L.GeoJSON();
var layersControl = new L.Control.Layers(baseMaps);
map.addControl(layersControl);

function makePointLayer(data) {
    pointGeoJSON.addData(data);
    pointGeoJSON.addTo(map);
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
