from django.test import TestCase, Client


class AboutURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.templates = {
            '/about/author.html': '/about/author/',
            '/about/tech.html': '/about/tech/',
        }

    def test_urls_about_exists_for_all(self):
        for reverse_name in self.templates.values():
            with self.subTest():
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)
