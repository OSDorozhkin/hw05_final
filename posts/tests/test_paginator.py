from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group

User = get_user_model()


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.guest_client = Client()
        user = User.objects.create(username='pushkin')
        group_obj = Group.objects.create(title='Тестовая группа',
                                         slug='test-slug')
        number_of_posts = 13
        posts = [
            Post(
                text=f'Тестовый текст {post_num}',
                author=user,
                group=group_obj
            )
            for post_num in range(number_of_posts)
        ]
        Post.objects.bulk_create(posts)

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10."""
        response = self.client.get(reverse('index'))
        self.assertEqual(len(response.context.get('page').object_list), 10)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(reverse('index') + '?page=2')
        self.assertEqual(len(response.context.get('page').object_list), 3)
