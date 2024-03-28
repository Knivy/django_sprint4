from django.contrib import admin  # type: ignore
from django.urls import include, path  # type: ignore
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm  # type: ignore
from django.views.generic.edit import CreateView  # type: ignore
from django.conf.urls.static import static  # type: ignore
from . import settings


urlpatterns: list[path] = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),
    path('posts/', include('blog.urls')),
    path('category/', include('blog.urls')),
    path('pages/', include('pages.urls')),
    path('auth/registration/',
         CreateView.as_view(
             template_name='registration/registration_form.html',
             form_class=UserCreationForm,
             success_url=reverse_lazy('blog:index'),
         ), name='registration'),
    path('auth/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_failure'
