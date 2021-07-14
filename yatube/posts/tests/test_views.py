import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls.base import reverse

from ..forms import PostForm
from ..models import Follow, Group, Post

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        settings.MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Lion',
            slug='lion',
            description='Lions fans are here',
        )
        cls.author = User.objects.create_user(
            username='LionUser'
        )
        cls.non_author = User.objects.create_user(
            username='LionUserFan'
        )
        cls.post = Post.objects.create(
            text='Some text about lions',
            author=cls.author,
            group=cls.group,
            image=cls.image,
        )
        cls.follow = Follow.objects.create(
            user=cls.non_author,
            author=cls.author,
        )
        cls.url_index = reverse('index')
        cls.url_follow_index = reverse('follow_index')
        cls.url_comment = reverse(
            'add_comment',
            kwargs={'username': cls.author.username, 'post_id': cls.post.id}
        )
        cls.follow_urls = (
            reverse('profile_follow',
                    kwargs={'username': cls.author.username}),
            reverse('profile_unfollow',
                    kwargs={'username': cls.author.username}),
        )
        cls.public_urls = (
            (cls.url_index, 'posts/index.html'),
            (reverse('group_posts', kwargs={'slug': cls.group.slug}),
             'posts/group.html'),
        )
        cls.private_urls = (
            (reverse('new_post'), 'posts/new_post.html'),
        )
        cls.paginator_pages = (
            reverse('index'),
            reverse('group_posts', kwargs={'slug': cls.group.slug}),
            reverse('profile', kwargs={'username': cls.author.username}),
        )

    def setUp(self):
        self.guest_clent = Client()
        self.post_author_client = Client()
        self.non_author = Client()
        self.post_author_client.force_login(ViewsTests.author)
        self.non_author.force_login(ViewsTests.non_author)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def check_context_fields(self, response, type):
        if type == 'page':
            first_object = response.context[type][0]
        else:
            first_object = response.context[type]
        post_text = first_object.text
        post_author = first_object.author
        post_group = first_object.group
        self.assertEqual(post_text, ViewsTests.post.text)
        self.assertEqual(post_author, ViewsTests.author)
        self.assertEqual(post_group, ViewsTests.group)
        self.assertContains(response, '<img')

    def test_pages_uses_correct_template(self):
        for reverse_name, template in (
            ViewsTests.public_urls + ViewsTests.private_urls
        ):
            with self.subTest(template=template):
                response = self.post_author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        response = self.post_author_client.get(ViewsTests.url_index)
        self.check_context_fields(response=response, type='page')

    def test_group_context(self):
        response = self.post_author_client.get(
            reverse('group_posts', kwargs={'slug': ViewsTests.group.slug})
        )
        self.check_context_fields(response=response, type='page')

    def test_post_relation_to_group(self):
        response = self.post_author_client.get(
            reverse('group_posts', kwargs={'slug': ViewsTests.group.slug})
        )
        self.check_context_fields(response=response, type='page')

    def test_profile_context(self):
        response = self.post_author_client.get(reverse(
            'profile', kwargs={'username': ViewsTests.author.username}
        ))
        self.check_context_fields(response=response, type='page')

    def test_post_view_context(self):
        response = self.post_author_client.get(reverse('post', kwargs={
            'username': ViewsTests.post.author.username,
            'post_id': ViewsTests.post.id,
        }))
        self.check_context_fields(response=response, type='post')

    def test_new_post_context(self):
        response = self.post_author_client.get(reverse('new_post'))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_edit_post_context(self):
        response = self.post_author_client.get(reverse('post_edit', kwargs={
            'username': ViewsTests.author.username,
            'post_id': ViewsTests.post.id,
        }))
        self.assertIsInstance(response.context['form'], PostForm)

    def test_paginator(self):
        spare = 3
        post_list = [
            Post(
                text='Some random test text',
                author=ViewsTests.author,
                group=ViewsTests.group
            ) for _ in range(
                settings.PAGES_AMOUNT + spare - 1
            )
        ]
        Post.objects.bulk_create(post_list)
        for reverse_name in ViewsTests.paginator_pages:
            with self.subTest(reverse_name=reverse_name):
                response = self.post_author_client.get(reverse_name)
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    settings.PAGES_AMOUNT
                )
                response = self.post_author_client.get(
                    reverse_name + '?page=2'
                )
                self.assertEqual(
                    len(response.context.get('page').object_list),
                    spare
                )

    def test_cache_index(self):
        Post.objects.create(
            text='Test cache post',
            author=ViewsTests.author,
        )
        response = self.post_author_client.get(reverse('index'))
        cache_before = response.content
        Post.objects.create(
            text='Test cache post 2',
            author=ViewsTests.author,
        )
        response = self.post_author_client.get(reverse('index'))
        cache_after = response.content
        self.assertEqual(cache_before, cache_after)

    def test_authorized_user_comment(self):
        response = self.guest_clent.get(ViewsTests.url_comment)
        self.assertNotEqual(response.status_code, HTTPStatus.OK)

    def new_post_only_for_followers(self):
        test_post = Post.objects.create(
            text='Test post for followers',
            author=ViewsTests.author,
        )
        response = self.non_author.get(ViewsTests.url_follow_index)
        first_object = response.context['page'][0]
        self.assertEqual(first_object.text, test_post.text)

    def test_authorized_user_follow_unfollow(self):
        for follow_url in ViewsTests.follow_urls:
            with self.subTest(follow_url=follow_url):
                response = self.guest_clent.get(follow_url)
                self.assertNotEqual(response.status_code, HTTPStatus.OK)
