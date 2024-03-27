from django.shortcuts import render  # type: ignore
from django.http import HttpResponse  # type: ignore
from django.views.generic import TemplateView  # type: ignore


class About(TemplateView):
    """Описание проекта."""

    template_name: str = 'pages/about.html'


class Rules(TemplateView):
    """Правила проекта."""

    template_name: str = 'pages/rules.html'


def page_not_found(request, exception) -> HttpResponse:
    """Ошибка 404: Страница не найдена."""
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason='') -> HttpResponse:
    """Ошибка 403: Ошибка CSRF токена."""
    return render(request, 'pages/403csrf.html', status=403)


def server_failure(request) -> HttpResponse:
    """Ошибка 500: Ошибка сервера."""
    return render(request, 'pages/500.html', status=500)
