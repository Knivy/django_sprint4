from django.urls import path  # type: ignore[import-untyped]

from . import views

app_name: str = 'pages'

urlpatterns: list[path] = [
    path('about/', views.about, name='about'),
    path('rules/', views.rules, name='rules'),
]

handler404 = 'views.page_not_found'
handler500 = 'views.server_failure'
