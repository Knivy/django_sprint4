from django.urls import include, path  # type: ignore[import-untyped]

from . import views

app_name: str = 'blog'

post_id_patterns: list[path] = [
    path('', views.PostDetailView.as_view(), name='post_detail'),
    path('edit/', views.PostUpdateView.as_view(), name='edit_post'),
    path('comment/', views.CommentCreateView.as_view(),
         name='add_comment'),
    path('edit_comment/<int:comment_id>/',
         views.CommentUpdateView.as_view(), name='edit_comment'),
    path('delete/', views.PostDeleteView.as_view(),
         name='delete_post'),
    path('delete_comment/<int:comment_id>/',
         views.CommentDeleteView.as_view(), name='delete_comment'),
]

urlpatterns: list[path] = [
    path('', views.IndexListView.as_view(), name='index'),
    path('category/<slug:category_slug>/', views.CategoryListView.as_view(),
         name='category_posts'),
    path('profile/edit/', views.ProfileUpdateView.as_view(),
         name='edit_profile'),
    path('profile/<slug:name_slug>/', views.ProfileListView.as_view(),
         name='profile'),
    path('posts/create/', views.PostCreateView.as_view(), name='create_post'),
    path('posts/<int:post_id>/', include(post_id_patterns)),
]
