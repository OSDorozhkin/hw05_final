import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Group, Post, Follow

User = get_user_model()
USERNAME1 = 'pushkin'
USERNAME2 = 'gogol'
SLUG1 = 'test_slug1'
SLUG2 = 'test_slug2'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL1 = reverse('group_page', kwargs={'slug': SLUG1})
GROUP_URL2 = reverse('group_page', kwargs={'slug': SLUG2})
PROFILE_URL1 = reverse('profile', kwargs={'username': USERNAME1})
PROFILE_URL2 = reverse('profile', kwargs={'username': USERNAME2})
FOLLOW_URL = reverse('follow_index')
PROFILE_FOLLOW_URL = reverse('profile_follow', kwargs={'username': USERNAME1})
PROFILE_UNFOLLOW_URL = reverse('profile_unfollow',
                               kwargs={'username': USERNAME1})
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client1 = Client()
        self.authorized_client2 = Client()
        self.user1 = User.objects.create(username=USERNAME1)
        self.user2 = User.objects.create(username=USERNAME2)
        self.authorized_client1.force_login(self.user1)
        self.authorized_client2.force_login(self.user2)
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        Group.objects.create(
            title='Имя группы',
            description='Текст',
            slug=SLUG1,
        )
        self.group_obj2 = Group.objects.create(
            title='Название',
            description='Описание',
            slug=SLUG2,
        )
        self.post = Post.objects.create(
            text='Тестовый текст',
            author=self.user2,
            group=self.group_obj2,
            image=uploaded
        )
        Follow.objects.create(
            user=self.user1,
            author=self.user2,
        )
        self.post_edit_url = reverse(
            'post_edit', kwargs={'username': USERNAME2,
                                 'post_id': self.post.id})
        self.post_url = reverse('post', kwargs={'username': USERNAME2,
                                                'post_id': self.post.id})
        self.templates_pages_name_no_form = {
            INDEX_URL: ('index.html', 'page'),
            GROUP_URL2: ('group.html', 'page'),
            PROFILE_URL2: ('profile.html', 'page'),
            FOLLOW_URL: ('follow.html', 'page')
        }
        self.templates_pages_name_post = {
            self.post_url: ('post.html', 'post'),
        }
        self.templates_pages_name_form = {
            NEW_POST_URL: ('new_post.html', 'form'),
            self.post_edit_url: ('new_post.html', 'form'),
        }

    def test_new_page_show_correct_context(self):
        """Проверка словаря контекста страницы создания поста."""
        response = self.authorized_client2.get(NEW_POST_URL)
        context = self.templates_pages_name_form[NEW_POST_URL][1]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(context).fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Проверка словаря контекста страницы редактирования поста."""
        response = self.authorized_client2.get(self.post_edit_url)
        context = self.templates_pages_name_form[self.post_edit_url][1]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get(context).fields.get(value)
                self.assertIsInstance(form_field, expected)

    @override_settings(CACHES={
        'default': {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    def test_pages_show_correct_context(self):
        """
        Проверяем, что словарь context страниц содержит ожидаемые значения.

        Так же что, при создании поста, он появляется на главной, в группе, в
        профайле и на странице поста.
        """
        for reverse_name, context in self.templates_pages_name_no_form.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client1.get(reverse_name)
                self.assertEqual(response.context.get(
                    context[1])[0].text, self.post.text)
                self.assertEqual(response.context.get(
                    context[1])[0].group.title, self.post.group.title)
                self.assertEqual(response.context.get(
                    context[1])[0].author.username, self.post.author.username)
                self.assertEqual(response.context.get(
                    context[1])[0].image, self.post.image)

    def test_post_page_show_correct_context(self):
        """Проверка словаря контекста страницы поста."""
        for reverse_name, context in self.templates_pages_name_post.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client1.get(reverse_name)
                self.assertEqual(response.context.get(
                    context[1]).text, self.post.text)
                self.assertEqual(response.context.get(
                    context[1]).group.title, self.post.group.title)
                self.assertEqual(response.context.get(
                    context[1]).author.username, self.post.author.username)
                self.assertEqual(response.context.get(
                    context[1]).image, self.post.image)

    def test_group_pages_show_correct_posts(self):
        """Чекаем, что пост не попал в группу, для которой не предназначен."""
        response = self.authorized_client1.get(GROUP_URL1)
        self.assertIsNone(response.context.get('post'))

    def test_index_cash(self):
        """ Проверка кэширования главной страницы """
        html_0 = self.guest_client.get(INDEX_URL)
        Post.objects.create(
            text='Тестовый текст2',
            author=self.user1,
            group=self.group_obj2,
        )
        html_1 = self.guest_client.get(INDEX_URL)
        self.assertHTMLEqual(str(html_0.content), str(html_1.content))
        cache.clear()
        html_0 = self.guest_client.get(INDEX_URL)
        self.assertHTMLNotEqual(str(html_0.content), str(html_1.content))

    def test_following_and_unfollowing(self):
        """Авторизованный пользователь может подписываться и отписываться."""
        response = self.authorized_client2.get(PROFILE_FOLLOW_URL)
        follow = self.user2.follower.get(author=self.user1)
        self.assertRedirects(response, PROFILE_URL1)
        self.assertEqual(follow.author, self.user1, 'Подписка не создалась')
        count_follow1 = self.user2.follower.filter(author=self.user1).count()
        response = self.authorized_client2.get(PROFILE_UNFOLLOW_URL)
        count_follow2 = self.user2.follower.filter(author=self.user1).count()
        self.assertRedirects(response, PROFILE_URL1)
        self.assertNotEqual(count_follow1, count_follow2,
                            'Не получилось отписаться')

    def test_follow_show_correct_posts(self):
        """Проверка добавления новой записи в подписки."""
        Follow.objects.create(
            user=self.user2,
            author=self.user1,
        )
        following_post = Post.objects.create(
            text='Тест подписок',
            author=self.user1,
            group=self.group_obj2,
        )
        response1 = self.authorized_client2.get(FOLLOW_URL)
        response2 = self.authorized_client1.get(FOLLOW_URL)
        self.assertEqual(response1.context.get('post'), following_post)
        self.assertNotEqual(response2.context.get('post'), following_post)
