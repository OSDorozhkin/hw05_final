from django.test import Client, TestCase
from django.urls import reverse


class AboutPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates = {
            'about/author.html': reverse('about:author'),
            'about/tech.html': reverse('about:tech')
        }

    def test_about_pages_uses_correct_template(self):
        for template, reverse_name in self.templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
