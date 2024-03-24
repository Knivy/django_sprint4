from django.contrib import admin  # type: ignore[import-untyped]
from django.urls import include, path

urlpatterns: list[path] = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('posts/', include('blog.urls')),
    path('category/', include('blog.urls')),
    path('pages/', include('pages.urls')),
]
