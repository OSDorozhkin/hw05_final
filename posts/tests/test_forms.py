import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()
USERNAME = 'pushkin'
SLUG = 'test_slug'
INDEX_URL = reverse('index')
NEW_POST_URL = reverse('new_post')
GROUP_URL = reverse('group_page', kwargs={'slug': SLUG})
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')


class PostFormTests(TestCase):
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
        self.user = User.objects.create_user(username=USERNAME)
        self.authorized_client.force_login(self.user)
        self.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        self.group_obj = Group.objects.create(
            title='Имя группы',
            description='Текст',
            slug=SLUG,
        )
        self.post = Post.objects.create(
            text='1. Тестовый текст без изменений',
            author=self.user,
            group=self.group_obj,
        )
        self.post_edit_url = reverse(
            'post_edit', kwargs={'username': self.user.username,
                                 'post_id': self.post.id}
        )
        self.add_comment_url = reverse(
            'add_comment', kwargs={'username': self.user.username,
                                   'post_id': self.post.id}
        )
        self.post_url = reverse(
            'post', kwargs={'username': self.user.username,
                            'post_id': self.post.id}
        )

    def test_create_new_post_form(self):
        """Тест формы создания нового поста."""
        posts_count = Post.objects.count() + 1
        form_data = {
            'text': 'Тестовый текст',
            'group': self.group_obj.id,
            'image': self.uploaded,
        }
        response = self.authorized_client.post(
            NEW_POST_URL,
            data=form_data,
            follow=True,
        )
        self.assertEquals(Post.objects.count(), posts_count)
        self.assertRedirects(response, INDEX_URL)

    def test_edit_post_form(self):
        """Тест формы редактирования поста."""
        posts_count = Post.objects.count()
        form_data = {
            'text': '2. Тестовый текст + изменения',
            'group': self.group_obj.id
        }
        response = self.authorized_client.post(
            self.post_edit_url,
            data=form_data,
            follow=True,
        )
        post = Post.objects.get(id=self.post.id).text
        self.assertEquals(post, form_data['text'])
        self.assertRedirects(response, self.post_url)
        self.assertEquals(Post.objects.count(), posts_count)

    def test_comment_post_form(self):
        """
        Тест формы Написания комментариев.

        Тестируем что только авторизированный пользователь может оставлять
        комментарии.
        """
        form_data_auth = {
            'text': 'Коммент аторизированного пользователя'
        }
        form_data_guest = {
            'text': 'Коммент неавторизованного пользователя'
        }
        self.authorized_client.post(
            self.add_comment_url,
            data=form_data_auth,
            follow=True,
        )
        comm_count_auth = self.post.comments.count()
        self.assertEqual(comm_count_auth, 1, 'Коммент не отправился')
        self.guest_client.post(
            self.add_comment_url,
            data=form_data_guest,
            follow=True,
        )
        comm_count_guest = self.post.comments.count()
        self.assertEqual(comm_count_guest, 1, 'Коммент отправился')
