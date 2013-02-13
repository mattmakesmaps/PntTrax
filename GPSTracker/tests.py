"""
Setting up basic test cases.
Called using manage.py and specifying the test.py settings extension.
(virtualenv)$ python manage.py test GPSTracker

Using coverage.py
(virtualenv)$ coverage run manage.py test GPSTracker # Execute Tests
(virtualenv)$ coverage html --include="/Users/matt/PycharmProjects/PntTrax/GPSTracker*" --omit="admin.py" # Gen HTML
"""

import os
from django.test import TestCase, Client
from file_uploads import save_zip

class ExampleTest(TestCase):
    fixtures = ['initial_data.json',]

    def setUp(self):
        """
        Create a client
        """
        self.client = Client()

    def test_response(self):
        # Issue a GET request.
        APP_ROOT = '/gpstracker'
        URLS = ['about', 'clients', 'groups', 'uploadfile']
        for url in URLS:
            response = self.client.get(os.path.join(APP_ROOT, url+'/'))
            # Check that the response is 200 OK.
            self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 200)

class FileUploads(TestCase):
    """
    Test file_uploads.py methods.
    """
    def setUp(self):
        upload_dir = os.environ['UPLOAD_DIR']
        # If our test data exists in the upload directory, delete it.
        if os.path.isfile(os.path.join(upload_dir, 'QGIS_lines.zip')):
            os.remove(os.path.join(upload_dir,'QGIS_lines.zip'))

        self.client = Client()

    def test_save_zip(self):
        """
        Test that the file validator is working properly.
        """
        # TODO Replace with environment variable to create relative path to fixture dir.
        with open('/Users/matt/PycharmProjects/PntTrax/GPSTracker/fixtures/QGIS_Lines.zip') as goodSHP:
            response = self.client.post('/gpstracker/uploadfile/', {'file':goodSHP})
            self.assertEqual(response.status_code, 302)

        with open('/Users/matt/PycharmProjects/PntTrax/GPSTracker/fixtures/NotAZip.shp') as notAZip:
            response = self.client.post('/gpstracker/uploadfile/', {'file':notAZip})
            self.assertEqual(response.status_code, 200)
            self.assertRaises(AssertionError)

        with open('/Users/matt/PycharmProjects/PntTrax/GPSTracker/fixtures/TwoSHPs.zip') as twoSHPs:
            response = self.client.post('/gpstracker/uploadfile/', {'file':twoSHPs})
            self.assertEqual(response.status_code, 200)
            self.assertRaises(AssertionError)

        with open('/Users/matt/PycharmProjects/PntTrax/GPSTracker/fixtures/ZipNoShp.zip') as zipNoShp:
            response = self.client.post('/gpstracker/uploadfile/', {'file':zipNoShp})
            self.assertEqual(response.status_code, 200)
            self.assertRaises(AssertionError)
