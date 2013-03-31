# Create your views here.
#from vectorformats.Formats import Django, GeoJSON
from django.contrib.auth.decorators import login_required, user_passes_test
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

@login_required
def clients(request):
    """Return a list of clients."""
    if request.user.is_staff:
        # Staff can view all clients.
        client_list = Client.objects.all()
        gps_group_list = Group.objects.all()
    else:
        # Filter clients and GPS Groups based on a user's group
        client_list = Client.objects.filter(gpsuser=request.user)
        # Group list filtered by client_list
        gps_group_list = Group.objects.filter(client__name__in=client_list)

    return render_to_response('gpstracker/clients.html', {'client_list': client_list, 'group_list': gps_group_list}, context_instance=RequestContext(request))

@login_required
def group(request, client_id):
    """Returns the GPS groups related to the selected client"""
    # If a user is staff, they can view all clients.
    # If not, get a list of clients that a user is associated with.
    # Compare that to the client object retrieved via Client.objects.get(pk=client_id)
    if request.user.is_staff or Client.objects.get(pk=client_id) in Client.objects.filter(gpsuser=request.user):
        client_selected = Client.objects.get(pk=client_id)
        group_list = Group.objects.filter(client__pk=client_id)
        return render_to_response('gpstracker/group.html', {'client_selected': client_selected, 'group_list': group_list}, context_instance=RequestContext(request))
    else:
        return render_to_response('gpstracker/unauthorized.html', context_instance=RequestContext(request))

@login_required
def group_detail(request, group_id):
    """Return a list of GPS Features for a GPS Group."""
    # Using a group_id, get the corresponding client object.
    # Check if a user is authorized to view data for that client.
    if Client.objects.get(group__pk=group_id) in Client.objects.filter(gpsuser=request.user):
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
    else:
        return render_to_response('gpstracker/unauthorized.html', context_instance=RequestContext(request))

@login_required
def geom_export(request, feat_id, geom_type, geom_format, group=False):
    """Return a serialized representation of geom and properties from a Django GeoQuerySet"""
    ## Grab appropriate model
    modelMap = {'point':(Point, 'group__point__pk'),'line':(Line, 'group__line__pk'),'poly':(Poly, 'group__poly__pk')}
    if geom_type.lower() in modelMap.keys():
        # Test if we're dealing with a geom group, or a individual geom
        if group and Client.objects.get(group__pk=feat_id) in Client.objects.filter(gpsuser=request.user):
            geom_rep = modelMap[geom_type][0].objects.filter(group__pk=feat_id)
        # Using keyword argument dictionary allows keyword parameters to be dynamicallys set.
        elif not group and Client.objects.get(**{modelMap[geom_type][1]:feat_id}) in Client.objects.filter(gpsuser=request.user):
            geom_rep = modelMap[geom_type][0].objects.filter(pk=feat_id)
        else:
            return HttpResponse('{WARNING: Unauthorized Resource Requested.}', content_type="text/plain")

    geom_out = djangoToExportFormat(request, geom_rep, format=geom_format)
    # If exporting a KML, Add MIME TYPE https://developers.google.com/kml/documentation/kml_tut#kml_server
    if geom_format.lower() == 'kml':
        # Requires Content-Disposition type:
        # https://docs.djangoproject.com/en/dev/ref/request-response/#telling-the-browser-to-treat-the-response-as-a-file-attachment
        # Corrects partial download error in firefox.
        response = HttpResponse(geom_out, content_type="application/vnd.google-earth.kml+xml")
        response['Content-Disposition'] = 'attachment; filename="kml_out.kml"'
    else:
        # Assume a text format, set response header for 'text/plain'
        return HttpResponse(geom_out, content_type="text/plain")

@login_required
def uploadfile1(request):
    """
    Present user with file upload screen...
    if successful, send them to a second form page to begin field mapping.
    if unsuccessful, have them retry.
    """
    if request.user.is_staff:
        if request.method == 'POST':
            form = uploadFileForm1(request.POST, request.FILES)
            if form.is_valid():
                cd = form.cleaned_data
                # DO SOMETHING WITH CLEAN DATA
                shpPath = preprocess_shapefile(cd)
                request.session['shpPath'] = shpPath
                return HttpResponseRedirect('./2')
            else:
                print form.errors
        else:
            form = uploadFileForm1()
        return render_to_response('gpstracker/uploadfile1.html', {'form': form}, context_instance=RequestContext(request))
    else:
        return render_to_response('gpstracker/unauthorized.html', context_instance=RequestContext(request))

@login_required
def uploadfile2(request):
    """
    Associate fields from a successfully parsed SHP with model fields.
    """
    if request.user.is_staff:
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
    else:
        return render_to_response('gpstracker/unauthorized.html',context_instance=RequestContext(request))

@login_required
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
