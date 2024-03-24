from django.urls import path  # type: ignore[import-untyped]

from . import views

app_name: str = 'blog'

urlpatterns: list[path] = [
    path('', views.IndexListView.as_view, name='index'),
    path('posts/<int:id>/', views.PostDetailView.as_view, name='post_detail'),
    path('category/<slug:category_slug>/', views.CategoryListView.as_view,
         name='category_posts'),
    path('profile/<int:pk>/', views.ProfileListView.as_view, name='profile'),
    path('posts/create/', views.PostCreateView.as_view, name='create'),
    path('posts/<int:post_id>/edit/', 
         views.PostUpdateView.as_view, name='edit'),
]
