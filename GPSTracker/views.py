# Create your views here.
#from vectorformats.Formats import Django, GeoJSON
from GPSTracker.models import Client, Group, Report, Point, Line, Poly
from django.http import HttpResponse
from django.template import Context, RequestContext, loader
from django.shortcuts import render_to_response

# Project Shortcuts
from shortcuts import djangoToGeoJSON

def index(request):
    return render_to_response('GPSTracker/index.html',{},context_instance=RequestContext(request))

def about(request):
    return render_to_response('GPSTracker/about.html',{},context_instance=RequestContext(request))

def clients(request):
    """Return a list of clients."""
    client_list = Client.objects.all()
    group_list = Group.objects.all()
    return render_to_response('GPSTracker/clients.html', {'client_list': client_list, 'group_list': group_list}, context_instance=RequestContext(request))

def group(request):
    """Return a list of clients."""
    client_list = Client.objects.all()
    group_list = Group.objects.all()
    return render_to_response('GPSTracker/group.html', {'client_list': client_list, 'group_list': group_list}, context_instance=RequestContext(request))

def group_detail(request, group_id):
    """Return a list of GPS Features for a GPS Group."""
    group = Group.objects.get(pk=group_id)
    point_list = Point.objects.filter(group__pk = group_id)
    line_list = Line.objects.filter(group__pk = group_id)
    poly_list = Poly.objects.filter(group__pk = group_id)
    return render_to_response('GPSTracker/group_detail.html', {'group': group,'point_list': point_list, 'line_list': line_list, 'poly_list': poly_list}, context_instance=RequestContext(request))

def geojson(request, feat_id):
    """Return GeoJSON object representing requested feature."""
    # Split request path and grab appropriate model
    pathParts = request.path.split('/')
    modelMap = {'point':Point,'line':Line,'poly':Poly}
    for part in pathParts:
        if part in modelMap:
            geom_rep = modelMap[part].objects.filter(pk=feat_id)
    GeoJSON = djangoToGeoJSON(request, geom_rep)
    return HttpResponse(GeoJSON)

def geojson_group(request, feat_id):
    """Return GeoJSON object representing requested feature."""
    # Split request path and grab appropriate model
#    group = Group.objects.select_related().get(pk=feat_id)
    pathParts = request.path.split('/')
    modelMap = {'point':Point,'line':Line,'poly':Poly}
    for part in pathParts:
        if part in modelMap:
            geom_rep = modelMap[part].objects.filter(group__pk=feat_id)
    GeoJSON = djangoToGeoJSON(request, geom_rep)
    return HttpResponse(GeoJSON)
