from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(id=55)
        self.group_obj = Group.objects.create(
            title='Тестовая группа',
            slug='/test/')
        self.post = Post.objects.create(
            text='Тестовый текст объёмом больше пятнадцати символов',
            author=user,
            group=self.group_obj,
        )

    def test_text_label(self):
        post = self.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEquals(verbose, 'Текст поста')

    def test_text_help_text(self):
        post = self.post
        help_text = post._meta.get_field('text').help_text
        self.assertEquals(help_text, 'Введите текст поста')

    def test_group_label(self):
        post = self.post
        verbose = post._meta.get_field('group').verbose_name
        self.assertEquals(verbose, 'Группа')

    def test_group_help_text(self):
        post = self.post
        help_text = post._meta.get_field('group').help_text
        self.assertEquals(help_text, 'Выберите группу для публикации поста')

    def test_object_name_is_text_field(self):
        post = self.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))

    def test_object_name_is_title_field(self):
        group = self.group_obj
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))
