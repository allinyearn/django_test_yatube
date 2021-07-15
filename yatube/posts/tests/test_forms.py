import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(dir=settings.BASE_DIR))
class FormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Lion',
            slug='lion',
            description='Lions fans are here',
        )
        cls.author = User.objects.create_user(
            username='LionUser'
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(FormTests.author)
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    def test_new_post_exists(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Testing new post creation',
            'group': FormTests.group.id,
            'image': FormTests.uploaded,
        }
        self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        new_post = Post.objects.first()
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.author, FormTests.author)
        self.assertEqual(new_post.group.id, form_data['group'])

    def test_post_edited(self):
        old_post = Post.objects.create(
            text='Old not edited post',
            author=FormTests.author,
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Edited text',
        }
        edited_post = self.authorized_client.post(
            reverse('post_edit', kwargs={
                'username': old_post.author.username,
                'post_id': old_post.id,
            }),
            data=form_data,
            follow=True
        )
        self.assertNotEqual(old_post, edited_post)
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(Post.objects.first().text, form_data['text'])
        self.assertEqual(Post.objects.first().author, old_post.author)

    def test_form_fields(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)
