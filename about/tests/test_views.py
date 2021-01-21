from django.test import Client, TestCase
from django.urls import reverse

ABOUT_URL = reverse('about:author')
TECH_URL = reverse('about:tech')


class AboutPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates = {
            ABOUT_URL: 'about/author.html',
            TECH_URL: 'about/tech.html',
        }

    def test_about_pages_uses_correct_template(self):
        for reverse_name, template in self.templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
