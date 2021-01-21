from django.test import TestCase, Client
from django.urls import reverse

ABOUT_URL = reverse('about:author')
TECH_URL = reverse('about:tech')


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates = (ABOUT_URL, TECH_URL)

    def test_urls_about_exists_for_all(self):
        for reverse_name in self.templates:
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)
