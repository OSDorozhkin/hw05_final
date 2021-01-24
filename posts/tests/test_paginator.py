from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Post, Group, Follow
from . import constants as ct

User = get_user_model()


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.authorized_client = Client()
        user1 = User.objects.create(username=ct.USERNAME1)
        user2 = User.objects.create(username=ct.USERNAME2)
        self.authorized_client.force_login(user1)
        Follow.objects.create(user=user1, author=user2)
        group_obj = Group.objects.create(title='Тестовая группа',
                                         slug=ct.SLUG1)
        number_of_posts = 13
        posts = [
            Post(
                text=f'Тестовый текст {post_num}',
                author=user2,
                group=group_obj
            )
            for post_num in range(number_of_posts)
        ]
        Post.objects.bulk_create(posts)
        self.templates_pages_name = {
            'INDEX_URL': ct.INDEX,
            'GROUP_URL': ct.GROUP1,
            'PROFILE_URL': ct.PROFILE2,
            'FOLLOW_URL': ct.FOLLOW,
        }

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        for reverse_name in self.templates_pages_name.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context.get('page').object_list), 10
                )

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        for reverse_name in self.templates_pages_name.values():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                self.assertEqual(
                    len(response.context.get('page').object_list), 3
                )
