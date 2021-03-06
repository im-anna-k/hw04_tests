from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PostForm, CommentForm
from .models import Group, Post, User, Comment, Follow
from django.core.cache import cache

POSTS_PER_PAGE = 10


def index(request):
    paginator = cache.get("posts_paginator", None)
    if paginator is None:
        paginator = Paginator(Post.objects.all(), POSTS_PER_PAGE)
        cache.set("posts_paginator", paginator, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POSTS_PER_PAGE]
    paginator = Paginator(posts, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all()
    post_count = post_list.count
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'username': author,
        'paginator': paginator,
        'post_count': post_count
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.select_related('post')
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'form': form,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    title = '???????????????? ????????????'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author.username)
    context = {
        'form': form,
        'title': title
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    is_edit = True
    if request.user != post.author:
        form = PostForm(request.POST or None, instance=post)
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST, files=request.FILES or None, instance=post)
    if form.is_valid():
        post.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'is_edit': is_edit,
        'post': post
    }
    return render(request, 'posts/create_post.html', context)


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
    following_authors = request.user.following.values_list('author_id',
                                                           flat=True)
    posts_following = Post.objects.filter(author_id__in=following_authors)
    context = {
        'posts_following': posts_following,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author_following = get_object_or_404(User, username=username)
    if (
        Follow.objects.filter(author=author_following,
                              user=request.user).exists()
        or request.user == author_following
    ):
        return redirect('posts:profile', username=username)
    Follow.objects.create(
        user=request.user,
        author=author_following,
    )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author_following = get_object_or_404(User, username=username)
    if (
        Follow.objects.filter(author=author_following,
                              user=request.user).exists()
        or request.user == author_following
    ):
        return redirect('posts:profile', username=username)
    Follow.objects.filter(author=author_following, user=request.user).delete()
    return redirect('posts:profile', username=username)
