from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class ModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='LionUser',
        )
        cls.post = Post.objects.create(
            text='Some text about lions',
            author=cls.author,
        )
        cls.group = Group.objects.create(
            title='Lion',
            slug='lion',
            description='Lions fans are here',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='Test comment',
        )

    def test_post_str_method(self):
        post = ModelTests.post
        expected_object_name = post.text[:15]
        self.assertEqual(expected_object_name, str(post))

    def test_group_str_method(self):
        group = ModelTests.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))

    def test_comment_str_method(self):
        comment = ModelTests.comment
        expected_object_name = comment.text[:10]
        self.assertEqual(expected_object_name, str(comment))
