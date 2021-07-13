from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Lion',
            slug='lion',
            description='Lions fans are here',
        )
        cls.author = User.objects.create_user(username='LionUser')
        cls.post = Post.objects.create(
            text='Some text about lions',
            group=cls.group,
            author=cls.author,
        )
        cls.user = User.objects.create_user(username='MrNobody')
        cls.edit_url = f'/{cls.author.username}/{cls.post.id}/edit/'
        cls.public_urls = (
            ('/', 'posts/index.html'),
            (f'/group/{cls.group.slug}/', 'posts/group.html'),
            (f'/{cls.author.username}/', 'posts/profile.html'),
            (f'/{cls.author.username}/{cls.post.id}/', 'posts/post.html'),
        )
        cls.private_urls = (
            ('/new/', 'posts/new_post.html'),
            (cls.edit_url, 'posts/new_post.html'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.post_author_client = Client()
        self.authorized_client.force_login(PostsURLTests.user)
        self.post_author_client.force_login(PostsURLTests.author)

    def test_accessibility_of_public_pages(self):
        for url, _ in PostsURLTests.public_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_accessibility_of_private_pages(self):
        for url, _ in PostsURLTests.private_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertRedirects(
                    response,
                    response.url,
                    status_code=HTTPStatus.FOUND,
                    target_status_code=HTTPStatus.OK,
                    fetch_redirect_response=True
                )

    def test_edit_post_for_author(self):
        response = self.post_author_client.get(
            PostsURLTests.edit_url
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_nonauthor(self):
        response = self.authorized_client.get(
            PostsURLTests.edit_url
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_correctness_templates(self):
        for url, template in (
            PostsURLTests.public_urls + PostsURLTests.private_urls
        ):
            with self.subTest(url=url):
                response = self.post_author_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_404_error(self):
        response = self.post_author_client.get('/some_nonexisted_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'misc/404.html')
