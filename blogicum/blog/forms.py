from django import forms  # type: ignore

from .models import Comment, Post


class PostForm(forms.ModelForm):
    """Форма создания и редактирования публикации."""

    class Meta:
        model = Post
        exclude = ('author',)


class CommentForm(forms.ModelForm):
    """Форма создания и редактирования комментария."""

    class Meta:
        model = Comment
        exclude = ('author',)
