from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Group, Post, User


@cache_page(60 * 20)
def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, settings.PAGES_AMOUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/index.html', {'page': page})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.all()
    paginator = Paginator(post_list, settings.PAGES_AMOUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request, 'posts/group.html', {'group': group, 'page': page})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    profile_post_list = author.posts.all()
    paginator = Paginator(profile_post_list, settings.PAGES_AMOUNT)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'posts/profile.html',
        {'author': author, 'page': page}
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    author = post.author
    comments = post.comments.all()
    form = CommentForm()
    return render(
        request, 'posts/post.html', {
            'post': post,
            'author': author,
            'comments': comments,
            'form': form
        }
    )


@login_required
def new_post(request):
    is_new = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method == 'GET' or not form.is_valid():
        return render(
            request,
            'posts/new_post.html',
            {'form': form, 'is_new': is_new}
        )
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('index')


@login_required
def post_edit(request, username, post_id):
    is_new = False
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    if request.user != post.author:
        return redirect('post', username, post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post.save()
        return redirect('post', username, post_id)
    return render(
        request,
        'posts/new_post.html',
        {'form': form, 'post': post, 'is_new': is_new}
    )


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    comments = post.comments.all()
    form = CommentForm(
        request.POST or None
    )
    if request.method == 'GET' or not form.is_valid():
        return render(
            request,
            'posts/include/comments.html',
            {'form': form, 'post': post, 'comments': comments}
        )
    comment = form.save(commit=False)
    comment.author = request.user
    comment.post = post
    comment.save()
    return redirect('post', username, post_id)
