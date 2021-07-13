from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        error_messages = {
            'text': {
                'required': 'Введите текст'
            }
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        error_messages = {
            'text': {
                'required': 'Вы не написали комментарий'
            }
        }
