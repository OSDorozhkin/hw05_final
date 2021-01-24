from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Post, Group, Comment
from . import constants as ct

User = get_user_model()


class PostModelTest(TestCase):
    def setUp(self):
        user = User.objects.create(username=ct.USERNAME1)
        self.group_obj = Group.objects.create(
            title='Имя группы',
            description='Текст',
            slug=ct.SLUG1,
        )
        self.post = Post.objects.create(
            text='Тестовый текст объёмом больше пятнадцати символов',
            author=user,
            group=self.group_obj,
        )
        self.comment = Comment(
            post=self.post,
            author=user,
            text='Тестовый коммент объёмом больше пятнадцати символов',
        )

    def test_post_label(self):
        verbose = self.post._meta.get_field('text').verbose_name
        self.assertEquals(verbose, 'Текст поста')

    def test_text_help_text(self):
        help_text = self.post._meta.get_field('text').help_text
        self.assertEquals(help_text, 'Введите текст поста')

    def test_group_label(self):
        verbose = self.post._meta.get_field('group').verbose_name
        self.assertEquals(verbose, 'Группа')

    def test_group_help_text(self):
        help_text = self.post._meta.get_field('group').help_text
        self.assertEquals(help_text, 'Выберите группу для публикации поста')

    def test_comment_label(self):
        verbose = self.comment._meta.get_field('text').verbose_name
        self.assertEquals(verbose, 'Комментарий')

    def test_comment_help_text(self):
        help_text = self.comment._meta.get_field('text').help_text
        self.assertEquals(help_text, 'Введите текст комментария')

    def test_object_name_is_post_text_field(self):
        expected_object_name = self.post.text[:15]
        self.assertEquals(expected_object_name, str(self.post))

    def test_object_name_is_group_title_field(self):
        expected_object_name = self.group_obj.title
        self.assertEquals(expected_object_name, str(self.group_obj))

    def test_object_name_is_comment_text_field(self):
        expected_object_name = self.comment.text[:15]
        self.assertEquals(expected_object_name, str(self.comment))
