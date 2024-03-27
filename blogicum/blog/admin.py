from django.contrib import admin  # type: ignore[import-untyped]

from .models import Category, Comment, Location, Post


admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Post)
admin.site.register(Comment)
