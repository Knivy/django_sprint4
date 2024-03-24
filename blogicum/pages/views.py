from django.shortcuts import render  # type: ignore[import-untyped]
from django.http import HttpResponse  # type: ignore[import-untyped]


def about(request) -> HttpResponse:
    """Описание проекта."""
    template: str = 'pages/about.html'
    return render(request, template)


def rules(request) -> HttpResponse:
    """Правила проекта."""
    template: str = 'pages/rules.html'
    return render(request, template)


def page_not_found(request, exception) -> HttpResponse:
    """Ошибка 404: Страница не найдена."""
    return render(request, 'pages/404.html')


def csrf_failure(request, reason='') -> HttpResponse:
    """Ошибка 403: Ошибка CSRF токена."""
    return render(request, 'pages/403csrf.html', status=403)


def server_failure(request, exception) -> HttpResponse:
    """Ошибка 500: Ошибка сервера."""
    return render(request, 'pages/500.html')
