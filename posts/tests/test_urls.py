from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Group, Post
from . import constants as ct

User = get_user_model()


class PostURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()
        self.user1 = User.objects.create_user(username=ct.USERNAME1)
        self.user2 = User.objects.create(username=ct.USERNAME2)
        self.authorized_client1 = Client()
        self.authorized_client2 = Client()
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2.force_login(self.user2)
        group_obj = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовый текст',
            slug=ct.SLUG1
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user2,
            group=group_obj,
        )
        post_edit_url = reverse('post_edit', kwargs={'username': ct.USERNAME2,
                                                     'post_id': self.post.id})
        post_url = reverse('post', kwargs={'username': ct.USERNAME2,
                                           'post_id': self.post.id})
        self.templates_url_authorized_r = {
            post_edit_url: ('new_post.html', post_url)
        }
        self.templates_url_authorized = {
            ct.NEW_POST: ('new_post.html',
                          '/auth/login/?next=' + ct.NEW_POST),
            ct.FOLLOW: ('follow.html', '/auth/login/?next=' + ct.FOLLOW)
        }
        self.templates_url_guest = {
            ct.INDEX: ('index.html',),
            ct.GROUP1: ('group.html',),
            ct.PROFILE2: ('profile.html',),
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
