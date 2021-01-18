from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user1 = get_user_model().objects.create_user(username='Pushkin')
        self.user2 = User.objects.create(id=55, username='gogol')
        self.authorized_client1 = Client()
        self.authorized_client2 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2.force_login(self.user2)
        self.templates_url_authorized_r = {
            '/gogol/12/edit/': ('new_post.html', '/gogol/12/')
        }
        self.templates_url_authorized = {
            '/new/': ('new_post.html', '/auth/login/?next=/new/'),
        }
        self.templates_url_guest = {
            '/': ('index.html',),
            '/group/test-slug/': ('group.html',),
            '/gogol/12/': ('post.html',),
            '/gogol/': ('profile.html',),
        }
        group_obj1 = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug='test-slug'
        )
        self.post = Post.objects.create(
            id=12,
            text='Тестовый текст',
            author=self.user2,
            group=group_obj1,
        )

    def test_urls_uses_correct_template(self):
        """Проверка правильности возвращаемого шаблона."""
        templates_url_all = {**self.templates_url_guest,
                             **self.templates_url_authorized,
                             **self.templates_url_authorized_r}
        for reverse_name, template in templates_url_all.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client2.get(reverse_name)
                self.assertTemplateUsed(response, template[0])

    def test_new_url_redirect_anonymous_on_logon(self):
        """Проверяем редиректы для неавторизованного пользователя."""
        templates_url_all = {**self.templates_url_authorized,
                             **self.templates_url_authorized_r}
        for reverse_name, template in templates_url_all.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertRedirects(response, template[1])

    def test_urls_exists_for_all(self):
        """Проверяем доступность страниц для всех пользователей."""
        for reverse_name in self.templates_url_guest.keys():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_urls_exists_for_authorized(self):
        """Проверяем доступность страниц для владельца поста."""
        templates_url_all = {**self.templates_url_authorized,
                             **self.templates_url_authorized_r}
        for reverse_name in templates_url_all.keys():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client2.get(reverse_name)
                self.assertEqual(response.status_code, 200)

    def test_urls_no_exists_for_authorized(self):
        """Проверяем редирект для не владельца поста."""
        for reverse_name, template in self.templates_url_authorized_r.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client1.get(reverse_name,
                                                       follow=True)
                self.assertRedirects(response, template[1])

    def test_error_404(self):
        response = self.guest_client.get('/gogol/mogol/')
        self.assertEqual(response.status_code, 404)
