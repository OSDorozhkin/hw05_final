from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, Group, Follow

User = get_user_model()
USERNAME2 = 'gogol'
SLUG = 'test_slug'
INDEX_URL = reverse('index')
GROUP_URL = reverse('group_page', kwargs={'slug': SLUG})
PROFILE_URL = reverse('profile', kwargs={'username': USERNAME2})
FOLLOW_URL = reverse('follow_index')


class PaginatorViewsTest(TestCase):
    def setUp(self):
        self.authorized_client = Client()
        user1 = User.objects.create(username='pushkin')
        user2 = User.objects.create(username=USERNAME2)
        self.authorized_client.force_login(user1)
        Follow.objects.create(
            user=user1,
            author=user2
        )
        group_obj = Group.objects.create(title='Тестовая группа', slug=SLUG)
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
            'INDEX_URL': INDEX_URL,
            'GROUP_URL': GROUP_URL,
            'PROFILE_URL': PROFILE_URL,
            'FOLLOW_URL': FOLLOW_URL,
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
