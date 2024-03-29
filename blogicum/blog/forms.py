from django import forms  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore

from .models import Comment, Post

User = get_user_model()


class PostForm(forms.ModelForm):
    """Форма создания и редактирования публикации."""

    class Meta:
        model = Post
        exclude = ('author', 'comment_count', 'is_published')
        widgets = {
            'pub_date': forms.DateTimeInput(
                format=('%d.%m.%Y %H:%M'),
                attrs={'type': 'datetime'}),
        }


class CommentForm(forms.ModelForm):
    """Форма создания и редактирования комментария."""

    class Meta:
        model = Comment
        exclude = ('author', 'post', 'is_published')


class ProfileForm(forms.ModelForm):
    """Форма создания и редактирования профиля."""

    class Meta:
        model = User
        exclude = ('is_staff', 'groups',
                   'user_permissions',
                   'is_active', 'is_superuser',
                   'last_login', 'date_joined',
                   'username', 'password')
