from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()
USERNAME = 'gogol'
SLUG = 'test_slug'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group_page', kwargs={'slug': SLUG})
PROFILE_URL = reverse('profile', kwargs={'username': USERNAME})
FOLLOW_URL = reverse('follow_index')


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user1 = User.objects.create_user(username='Pushkin')
        self.user2 = User.objects.create(username=USERNAME)
        self.authorized_client1 = Client()
        self.authorized_client2 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2.force_login(self.user2)
        group_obj = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug=SLUG
        )
        self.post = Post.objects.create(
            id=12,
            text='Тестовый текст',
            author=self.user2,
            group=group_obj,
        )
        post_edit_url = reverse('post_edit', kwargs={'username': USERNAME,
                                                     'post_id': self.post.id})
        post_url = reverse('post', kwargs={'username': USERNAME,
                                           'post_id': self.post.id})
        self.templates_url_authorized_r = {
            post_edit_url: ('new_post.html', post_url)
        }
        self.templates_url_authorized = {
            NEW_POST_URL: ('new_post.html',
                           '/auth/login/?next=' + NEW_POST_URL),
            FOLLOW_URL: ('follow.html', '/auth/login/?next=' + FOLLOW_URL)
        }
        self.templates_url_guest = {
            INDEX_URL: ('index.html',),
            GROUP_URL: ('group.html',),
            PROFILE_URL: ('profile.html',),
            post_url: ('post.html',),
        }

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
        for reverse_name, redirect in templates_url_all.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name, follow=True)
                self.assertRedirects(response, redirect[1])

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
        for reverse_name, redirect in self.templates_url_authorized_r.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client1.get(reverse_name,
                                                       follow=True)
                self.assertRedirects(response, redirect[1])

    def test_error_404(self):
        response = self.guest_client.get('/gogol/mogol/')
        self.assertEqual(response.status_code, 404)
