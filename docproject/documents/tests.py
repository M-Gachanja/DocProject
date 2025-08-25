from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from .models import Document
import tempfile

class DocumentAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_file_upload(self):
        test_file = tempfile.NamedTemporaryFile(suffix='.pdf').name
        response = self.client.post(
            reverse('document-list'),
            {'title': 'Test Doc', 'file': test_file},
            format='multipart'
        )
        self.assertEqual(response.status_code, 201)

    def test_search(self):
        Document.objects.create(title='Test Doc', owner=self.user)
        response = self.client.get('/api/documents/?search=Test')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Doc')