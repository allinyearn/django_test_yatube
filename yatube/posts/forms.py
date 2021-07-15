from django import forms
from django.forms import Textarea

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
        widgets = {
            'text': Textarea(attrs={'rows': 4})
        }
        error_messages = {
            'text': {
                'required': 'Вы не написали комментарий'
            }
        }
