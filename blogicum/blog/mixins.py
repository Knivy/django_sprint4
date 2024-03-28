from django.contrib.auth.mixins import UserPassesTestMixin  # type: ignore
from django.shortcuts import redirect  # type: ignore


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверка на авторство."""

    def test_func(self):
        """Проверка на авторство."""
        object = self.get_object()
        return object.author == self.request.user

    def handle_no_permission(self):
        """Перенаправляет неавторов."""
        return redirect('blog:post_detail',
                        post_id=self.kwargs.get('post_id'))
