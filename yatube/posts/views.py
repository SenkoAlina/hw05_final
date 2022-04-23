from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import get_page_context


def index(request):

    post_list = Post.objects.select_related('author', 'group').all()
    context = get_page_context(post_list, request)

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    context = {
        'group': group,
    }
    context.update(get_page_context(post_list, request))

    return render(request, 'posts/group_list.html', context)


def profile(request, username):

    author = get_object_or_404(
        User.objects.select_related(), username=username)
    posts_of_author = author.posts.all()
    following = (
        request.user.is_authenticated
        and author.following.filter(user=request.user)
    )
    context = {
        'author': author,
        'following': following,
    }
    context.update(get_page_context(posts_of_author, request))

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):

    post = get_object_or_404(
        Post.objects.select_related('author', 'group'), id=post_id)
    form = CommentForm(request.POST or None)

    if request.method == 'POST':
        return redirect('posts: add_comment')
    comments = post.comments.all()
    context = {
        'post': post,
        'form': form,
        'comments': comments,
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None, files=request.FILES or None)

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()

        return redirect('posts:profile', username=post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):

    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:

        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)

    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': True, 'post': post})


@login_required
def add_comment(request, post_id):

    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):

    post_list = Post.objects.filter(author__following__user=request.user)
    context = get_page_context(post_list, request)

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):

    if request.user.username == username:

        return redirect('posts:profile', username=username)

    following = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(
        user=request.user,
        author=following
    )

    if not follow:
        Follow.objects.create(user=request.user, author=following)

    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):

    following = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, author=following, user=request.user)
    follow.delete()

    return redirect('posts:profile', username=username)
