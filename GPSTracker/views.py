# Create your views here.
from GPSTracker.models import Client, Group, Report, Point, Line, Poly
from django.http import HttpResponse
from django.template import Context, RequestContext, loader
from django.shortcuts import render_to_response

def index(request):
    return render_to_response('GPSTracker/index.html',{},context_instance=RequestContext(request))

def clients(request):
    """Return a list of clients."""
    client_list = Client.objects.all()
    group_list = Group.objects.all()
    return render_to_response('GPSTracker/clients.html', {'client_list': client_list, 'group_list': group_list}, context_instance=RequestContext(request))

def group_detail(request, group_id):
    """Return a list of GPS Features for a GPS Group."""
    point_list = Point.objects.filter(group__pk = group_id)
    line_list = Line.objects.filter(group__pk = group_id)
    poly_list = Poly.objects.filter(group__pk = group_id)
    return render_to_response('GPSTracker/group_detail.html', {'point_list': point_list, 'line_list': line_list, 'poly_list': poly_list}, context_instance=RequestContext(request))
