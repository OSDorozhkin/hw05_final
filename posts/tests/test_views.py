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
        self.authorized_client = Client()
        self.authorized_client2 = Client()
        self.user = User.objects.create(id=55, username='Pushkin')
        self.user2 = User.objects.create(username='gogol')
        self.authorized_client.force_login(self.user)
        self.authorized_client2.force_login(self.user2)
        small_gif = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
                     b'\x01\x00\x80\x00\x00\x00\x00\x00'
                     b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                     b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                     b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                     b'\x0A\x00\x3B')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        group_obj1 = Group.objects.create(
            title='Имя группы',
            description='Текст',
            slug='test-slug1',
        )
        self.group_obj2 = Group.objects.create(
            title='Название',
            description='Описание',
            slug='test-slug2',
        )
        self.post = Post.objects.create(
            id=0,
            text='Тестовый текст',
            author=self.user,
            group=group_obj1,
            image=uploaded
        )
        self.templates_pages_name_no_form = {
            'index.html': (reverse('index'), 'page'),
            'group.html': (reverse('group_page',
                                   kwargs={'slug': 'test-slug1'}), 'page'),
            'profile.html': (reverse('profile',
                                     kwargs={'username': 'Pushkin'}), 'page'),
        }
        self.templates_pages_name_post = {
            'post.html': (reverse('post',
                                  kwargs={'username': 'Pushkin',
                                          'post_id': 0}), 'post')
        }
        self.templates_pages_name_form = {
            'new_post.html': (reverse('new_post'), 'form')
        }

    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    def test_pages_uses_correct_template(self):
        """Проверяем используемые шаблоны."""
        templates_pages_name = {
            **self.templates_pages_name_no_form,
            **self.templates_pages_name_post,
            **self.templates_pages_name_form
        }
        for template, reverse_name in templates_pages_name.items():
            with self.subTest(reverse_name=reverse_name[0]):
                response = self.authorized_client.get(reverse_name[0])
                self.assertTemplateUsed(response, template)

    def test_new_page_show_correct_context(self):
        """Проверка словаря контекста страницы создания поста."""
        response = self.authorized_client.get(reverse('new_post'))
        context = self.templates_pages_name_form['new_post.html'][1]
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
        reverse_name = reverse('post_edit',
                               kwargs={'username': 'Pushkin', 'post_id': 0})
        response = self.authorized_client.get(reverse_name)
        context = self.templates_pages_name_form['new_post.html'][1]
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
        for reverse_name in self.templates_pages_name_no_form.values():
            with self.subTest(reverse_name=reverse_name[0]):
                response = self.authorized_client.get(reverse_name[0])
                self.assertEqual(response.context.get(
                    reverse_name[1])[0].text, self.post.text)
                self.assertEqual(response.context.get(
                    reverse_name[1])[0].group.title, self.post.group.title)
                self.assertEqual(response.context.get(
                    reverse_name[1])[0].author.username,
                                 self.post.author.username)
                self.assertEqual(response.context.get(
                    reverse_name[1])[0].image, self.post.image)

    def test_post_page_show_correct_context(self):
        """Проверка словаря контекста страницы поста."""
        for reverse_name in self.templates_pages_name_post.values():
            with self.subTest(reverse_name=reverse_name[0]):
                response = self.authorized_client.get(reverse_name[0])
                self.assertEqual(response.context.get(
                    reverse_name[1]).text, self.post.text)
                self.assertEqual(response.context.get(
                    reverse_name[1]).group.title, self.post.group.title)
                self.assertEqual(response.context.get(
                    reverse_name[1]).author.username,
                                 self.post.author.username)
                self.assertEqual(response.context.get(reverse_name[1]).image,
                                 self.post.image)

    def test_group_pages_show_correct_posts(self):
        """Чекаем, что пост не попал в группу, для которой не предназначен."""
        response = self.authorized_client.get(
            reverse('group_page', kwargs={'slug': 'test-slug2'})
        )
        self.assertIsNone(response.context.get('post'))

    def test_index_cash(self):
        """ Проверка кэширования главной страницы """
        html_0 = self.guest_client.get('/')
        Post.objects.create(
            text='Тестовый текст2',
            author=self.user,
            group=self.group_obj2,
        )
        html_1 = self.guest_client.get('/')
        self.assertHTMLEqual(str(html_0.content), str(html_1.content))
        cache.clear()
        html_0 = self.guest_client.get('/')
        self.assertHTMLNotEqual(str(html_0.content), str(html_1.content))

    def test_following_and_unfollowing(self):
        """Авторизованный пользователь может подписываться и отписываться."""
        response = self.authorized_client.get(
            reverse('profile_follow', kwargs={'username': self.user2})
        )
        follow = self.user.follower.get(author=self.user2)
        self.assertRedirects(response, '/gogol/')
        self.assertEqual(follow.author, self.user2, 'Подписка не создалась')
        count_follow1 = self.user.follower.filter(author=self.user2).count()
        response = self.authorized_client.get(
            reverse('profile_unfollow', kwargs={'username': self.user2})
        )
        count_follow2 = self.user.follower.filter(author=self.user2).count()
        self.assertRedirects(response, '/gogol/')
        self.assertNotEqual(count_follow1, count_follow2,
                            'Не получилось отписаться')

    def test_follow_show_correct_posts(self):
        """Проверка добавления новой записи в подписки."""
        Follow.objects.create(
            user=self.user,
            author=self.user2
        )
        following_post = Post.objects.create(
            text='Тест подписок',
            author=self.user2,
            group=self.group_obj2,
        )
        response1 = self.authorized_client.get(reverse('follow_index'))
        response2 = self.authorized_client2.get(reverse('follow_index'))
        self.assertEqual(response1.context.get('post'), following_post)
        self.assertNotEqual(response2.context.get('post'), following_post)
