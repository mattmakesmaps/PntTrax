from fiona import collection
import random

# Example cleaned data class from a validated form request.
class request:
    def rand_group(self):
        return random.randint(1,100)

    def __init__(self):
        self.cleaned_data = {'gps_group':self.rand_group()}

# Create the request
testReq = request()

# Open a data source (presumably something we've uploaded')
with collection("./data/Tribal_poly.shp", "r") as tribal_shp:
    #Loop through each feature, adding a group issued from the request
    for feat in tribal_shp:
        feat['properties']['gps_group'] = testReq.cleaned_data['gps_group']
        print feat['properties']['TRIBAL_NM1'], feat['properties']['gps_group']

