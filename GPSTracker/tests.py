"""
Setting up basic test cases.
Called using manage.py and specifying the test.py settings extension.
(virtualenv)$ python manage.py test GPSTracker

Using coverage.py
(virtualenv)$ coverage run manage.py test GPSTracker # Execute Tests
(virtualenv)$ coverage run manage.py test GPSTracker --settings=PntTrax.settings.tests
(virtualenv)$ coverage run manage.py test GPSTracker --settings=PntTrax.settings.tests --verbosity 2
(virtualenv)$ coverage html --include="/Users/matt/PycharmProjects/PntTrax/GPSTracker*" --omit="admin.py" # Gen HTML
"""

import os
from django.test import TestCase, Client


class GetPages(TestCase):
    fixtures = ['test_data.json', ]

    def setUp(self):
        """
        Create a client
        """
        self.client = Client()

    def test_response(self):
        # Issue a GET request.
        APP_ROOT = '/gpstracker'
        URLS = ['about', 'clients', 'groups', 'groups/1', 'uploadfile']
        for url in URLS:
            response = self.client.get(os.path.join(APP_ROOT, url + '/'))
            # Check that the response is 200 OK.
            self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)


class FileUploads(TestCase):
    """
    Test file_uploads.py methods.
    """
    fixtures = ['test_data.json', ]

    def setUp(self):
        self.upload_dir = os.environ['UPLOAD_DIR']
        # If our test data exists in the upload directory, delete it.
        if os.path.isfile(os.path.join(self.upload_dir, 'QGIS_lines.zip')):
            os.remove(os.path.join(self.upload_dir, 'QGIS_lines.zip'))

        self.client = Client()

    def test_validators(self):
        """
        Test that the file validator is working properly.
        """
        # TODO Replace with environment variable to create relative path to fixture dir.
        with open('/Users/matt/PycharmProjects/PntTrax/GPSTracker/fixtures/QGIS_Lines.zip') as goodSHP:
            response = self.client.post('/gpstracker/uploadfile/', {'file': goodSHP})
            self.assertEqual(response.status_code, 302)

        with open('/Users/matt/PycharmProjects/PntTrax/GPSTracker/fixtures/NotAZip.shp') as notAZip:
            response = self.client.post('/gpstracker/uploadfile/', {'file': notAZip})
            self.assertEqual(response.status_code, 200)
            self.assertRaises(AssertionError)

        with open('/Users/matt/PycharmProjects/PntTrax/GPSTracker/fixtures/TwoSHPs.zip') as twoSHPs:
            response = self.client.post('/gpstracker/uploadfile/', {'file': twoSHPs})
            self.assertEqual(response.status_code, 200)
            self.assertRaises(AssertionError)

        with open('/Users/matt/PycharmProjects/PntTrax/GPSTracker/fixtures/ZipNoShp.zip') as zipNoShp:
            response = self.client.post('/gpstracker/uploadfile/', {'file': zipNoShp})
            self.assertEqual(response.status_code, 200)
            self.assertRaises(AssertionError)

    def test_upload(self):
        """
        Test file upload works.
        """
        with open('/Users/matt/PycharmProjects/PntTrax/GPSTracker/fixtures/QGIS_Lines.zip') as goodSHP:
            self.client.post('/gpstracker/uploadfile/', {'file': goodSHP})

        response = self.client.post('/gpstracker/uploadfile/2',
                                    {'type': u'', 'collectDates': u'GPS_Date', 'comment': u'comment',
                                     'group': u'1', 'method': u'',
                                     'name': u'Feat_Name'})

        self.assertEqual(response.status_code, 302)


class GeomExport(TestCase):
    """
    Test Geom Export
    """
    fixtures = ['test_data.json', ]

    def setUp(self):
        """
        Create a client
        """
        self.client = Client()

    def test_geom_export(self):
        """
        Test KML and GeoJSON geometry exports for groups and individual features.
        """
        APP_ROOT = '/gpstracker'
        URLS = ['kml/line/1', 'geojson/line/1', 'kml/point/6', 'geojson/point/6', 'kml/poly/1', 'geojson/poly/1',
                'kml/point/group/1', 'geojson/point/group/1', 'kml/line/group/1', 'geojson/line/group/1',
                'kml/poly/group/2', 'geojson/poly/group/2']
        for url in URLS:
            response = self.client.get(os.path.join(APP_ROOT, url + '/'))
            # Check that the response is 200 OK.
            self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)

