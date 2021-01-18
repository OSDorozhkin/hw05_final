from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model


from .models import Post, Group, Follow
from .forms import PostForm, CommentForm

User = get_user_model()


def index(request):
    """
    Вью главной страницы.

    Выводит все посты, разбивая по страницам.
    """
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'index.html', {'paginator': paginator,
                                          'page': page})


def group_posts(request, slug):
    """
    Вью групп.

    Выводит посты относящиеся к одной группе, разбивая по страницам.
    """
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'group.html', {'paginator': paginator,
                                          'group': group, 'page': page})


@login_required
def new_post(request):
    """
    Вью формы создания нового поста.

    Выводит форму создания нового поста, при успешном создании переадресует
    на главную, страница не доступна неавторизированным пользователям.
    Использует один шаблон с вью редактирования поста, text_form
    передаёт нужный контест для оформления формы.
    """
    form = PostForm(request.POST or None)
    text_form = {
        'head': 'Добавить запись',
        'button': 'Добавить'
    }

    if form.is_valid():
        post_data = form.save(commit=False)
        post_data.author = request.user
        post_data.save()
        return redirect('index')

    return render(request, 'new_post.html', {'text_form': text_form,
                                             'form': form})


def profile(request, username):
    """
    Вью профиля авторов.

    Выводит все посты автора, разбивая по страницам. Так же статистику
    автора: число постов, число подписок, число подписчиков. Кнопка
    подписаться недоступна себе и неавторизованным пользователям.
    """
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    post_count = post_list.count()
    following_count = author.following.count()
    follower_count = author.follower.count()
    some_counts = {
        'post_count': post_count,
        'following_count': following_count,
        'follower_count': follower_count,
    }
    if str(request.user) != 'AnonymousUser' \
            and str(request.user) != str(author):
        following = author.following.filter(user=request.user).count()
        return render(request, 'profile.html', {'author': author,
                                                'page': page,
                                                'following': following,
                                                'some_counts': some_counts,
                                                'paginator': paginator})
    following = 2
    return render(request, 'profile.html', {'author': author,
                                            'page': page,
                                            'following': following,
                                            'some_counts': some_counts,
                                            'paginator': paginator})


def post_view(request, username, post_id):
    """
    Вью выбранного поста.

    Выводит пост, комменты к нему, форму написания нового коммента.
    read_button отключает кнопку комментарии в шаблоне поста.
    """
    form = CommentForm(request.POST or None)
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    post_count = author.posts.count()
    comments = post.comments.all()
    read_button = 1
    return render(request, 'post.html', {'author': author,
                                         'post_count': post_count,
                                         'post': post,
                                         'comments': comments,
                                         'form': form,
                                         'read_button': read_button})


def post_edit(request, username, post_id):
    """
    Вью формы редактирования поста.

    Страница доступна по кнопке редактирование под постом для
    автора этого поста, изначально поля формы заполнены.
    """
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=post)
    text_form = {
        'head': 'Редактировать запись',
        'button': 'Сохранить'
    }

    if author != request.user:
        return redirect('post', username, post_id)

    if form.is_valid():
        form.save()
        return redirect('post', username, post_id)

    return render(request, 'new_post.html', {'text_form': text_form,
                                             'form': form,
                                             'post': post})


@login_required
def add_comment(request, username, post_id):
    """
    Вью формы написания комментов к посту.

    Форма доступна для аторизованных пользователей.
    """
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, author=author, id=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        post_data = form.save(commit=False)
        post_data.author = request.user
        post_data.post = post
        post_data.save()
        return redirect('post', username, post_id)

    return render(request, 'post.html')


def page_not_found(request, exception):
    return render(request, 'misc/404.html', {'path': request.path}, status=404)


def server_error(request):
    return render(request, 'misc/500.html', status=500)


@login_required()
def follow_index(request):
    """
    Вью постов составленных из подписок.

    Страница доступна только авторизованным пользователям, разбита
    на страницы.
    """
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'follow.html', {'page': page,
                                           'paginator': paginator})


@login_required()
def profile_follow(request, username):
    """
    Вью кнопки подписаться на странице профиля.

    Доступна только если пользовательне подписан.
    """
    author = get_object_or_404(User, username=username)
    follow = request.user.follower.filter(author=author).count()
    if request.user != author and follow == 0:
        Follow.objects.create(
            user=request.user,
            author=author
        )
        return redirect('profile', username)
    return redirect('profile', username)


@login_required()
def profile_unfollow(request, username):
    """
    Вью кнопки отписаться на странице профиля.

    Кнопка доступна только пользователям, подписанным на автора.
    """
    author = get_object_or_404(User, username=username)
    user = request.user
    Follow.objects.filter(user=user, author=author).delete()
    return redirect('profile', username)
