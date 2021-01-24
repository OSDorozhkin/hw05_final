from django.urls import reverse

USERNAME1 = 'pushkin'
USERNAME2 = 'gogol'
SLUG1 = 'test_slug1'
SLUG2 = 'test_slug2'
INDEX = reverse('index')
NEW_POST = reverse('new_post')
GROUP1 = reverse('group_page', kwargs={'slug': SLUG1})
GROUP2 = reverse('group_page', kwargs={'slug': SLUG2})
PROFILE1 = reverse('profile', kwargs={'username': USERNAME1})
PROFILE2 = reverse('profile', kwargs={'username': USERNAME2})
FOLLOW = reverse('follow_index')
PROFILE_FOLLOW = reverse('profile_follow', kwargs={'username': USERNAME1})
PROFILE_UNFOLLOW = reverse('profile_unfollow',
                           kwargs={'username': USERNAME1})
SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')
