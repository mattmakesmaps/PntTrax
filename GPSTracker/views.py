# Create your views here.
#from vectorformats.Formats import Django, GeoJSON
from django.http import HttpResponse, HttpResponseRedirect
from django.template import Context, RequestContext, loader
from django.shortcuts import render_to_response
from .forms import uploadFileForm1, uploadFileForm2
from .models import Client, Group, Point, Line, Poly

from GPSTracker.file_uploads import preprocess_shapefile, import_shapefile

# Project Shortcuts
from shortcuts import djangoToExportFormat

def index(request):
    return render_to_response('gpstracker/index.html',{},context_instance=RequestContext(request))

def about(request):
    return render_to_response('gpstracker/about.html',{},context_instance=RequestContext(request))

def clients(request):
    """Return a list of clients."""
    client_list = Client.objects.all()
    group_list = Group.objects.all()
    return render_to_response('gpstracker/clients.html', {'client_list': client_list, 'group_list': group_list}, context_instance=RequestContext(request))

def clientsAuth(request):
    """Return a list of clients."""
    # Client.objects.get(name='City of Yakima')
    # request.user.groups.all()
    # request.user.groups.all()[0].name
    # request.user.groups.values_list()
    # Client.objects.get(name__in=['Makah','City of Yakima'])

    # Grab the groups a user is associated with
    group_list = []
    for group in request.user.groups.all():
        group_list.append(group.name)

    try:
        # Filter clients and GPS Groups based on a user's group
        client_list = Client.objects.filter(name__in=group_list)
        # Group list filtered by client_list
        gps_group_list = Group.objects.filter(client__name__in=group_list)
    except:
        pass
    return render_to_response('gpstracker/clients.html', {'client_list': client_list, 'group_list': gps_group_list}, context_instance=RequestContext(request))

def group(request):
    """Return a list of clients."""
    client_list = Client.objects.all()
    group_list = Group.objects.all()
    return render_to_response('gpstracker/group.html', {'client_list': client_list, 'group_list': group_list}, context_instance=RequestContext(request))

def group_detail(request, group_id):
    """Return a list of GPS Features for a GPS Group."""
    args = dict()
    args['group'] = Group.objects.get(pk=group_id)
    point_list = Point.objects.filter(group__pk = group_id)
    line_list = Line.objects.filter(group__pk = group_id)
    poly_list = Poly.objects.filter(group__pk = group_id)
    geom_dict = {'point_list':point_list,'line_list':line_list,'poly_list':poly_list}
    # Only send to render_to_response those geoms (point/line/poly) that exist
    for geom_key, geom_value in geom_dict.iteritems():
        if geom_value.exists():
            args[geom_key] = geom_value
    return render_to_response('gpstracker/group_detail.html', args, context_instance=RequestContext(request))

def geom_export(request, feat_id, geom_type, geom_format, group=False):
    """Return a serialized representation of geom and properties from a Django GeoQuerySet"""
    # Grab appropriate model
    modelMap = {'point':Point,'line':Line,'poly':Poly}
    if geom_type.lower() in modelMap.keys():
        # Test if we're dealing with a geom group, or a individual geom
        if group:
            geom_rep = modelMap[geom_type].objects.filter(group__pk=feat_id)
        elif not group:
            geom_rep = modelMap[geom_type].objects.filter(pk=feat_id)
    geom_out = djangoToExportFormat(request, geom_rep, format=geom_format)
    # If exporting a KML, Add MIME TYPE https://developers.google.com/kml/documentation/kml_tut#kml_server
    if geom_format.lower() == 'kml':
        # Requires Content-Disposition type:
        # https://docs.djangoproject.com/en/dev/ref/request-response/#telling-the-browser-to-treat-the-response-as-a-file-attachment
        # Corrects partial download error in firefox.
        response = HttpResponse(geom_out, content_type="application/vnd.google-earth.kml+xml")
        response['Content-Disposition'] = 'attachment; filename="kml_out.kml"'
        return response
    else:
        # Assume a text format, set response header for 'text/plain'
        return HttpResponse(geom_out, content_type="text/plain")

def uploadfile1(request):
    """
    Present user with file upload screen...
    if successful, send them to a second form page to begin field mapping.
    if unsuccessful, have them retry.
    """
    if request.method == 'POST':
        form = uploadFileForm1(request.POST, request.FILES)
        if form.is_valid():
            cd = form.cleaned_data
            # DO SOMETHING WITH CLEAN DATA
            shpPath = preprocess_shapefile(cd)
            request.session['shpPath'] = shpPath
            return HttpResponseRedirect('./2')
        #            return HttpResponseRedirect('../session/response')
        else:
            print form.errors
    else:
        form = uploadFileForm1()
    return render_to_response('gpstracker/uploadfile1.html', {'form': form} ,context_instance=RequestContext(request))

def uploadfile2(request):
    """
    Associate fields from a successfully parsed SHP with model fields.
    """
    if request.method == 'POST':
        # Required to repass shpPath kwarg
        form = uploadFileForm2(request.POST,shpPath=request.session['shpPath'])
        if form.is_valid():
            cd = form.cleaned_data
            # DO SOMETHING WITH CLEAN DATA
            import_shapefile(cd, request.session['shpPath'])
            return HttpResponseRedirect('./success')
        else:
            print form.errors
    else:
        form = uploadFileForm2(shpPath=request.session['shpPath'])
    return render_to_response('gpstracker/uploadfile2.html', {'form': form} ,context_instance=RequestContext(request))

def upload_success(request):
    """
    A file a has been successfully upload and processed into an appropriate model.
    """
    return render_to_response('gpstracker/upload_success.html', context_instance=RequestContext(request))

"""
Simple code to test usage of Django Sessions middleware.
"""
def session_request(request):
    myFile = 'path/to/shp'
    request.session['shpPath'] = myFile
    if 'filePath' in request.session:
        return HttpResponseRedirect('./response')

def session_response(request):
    if 'shpPath' in request.session:
        return HttpResponse('File Path: %s' % request.session['shpPath'])
    else:
        return HttpResponse('File Path Not Set')
