from datetime import datetime as dt  # type: ignore[import-untyped]

from django.db.models import QuerySet  # type: ignore[import-untyped]
from django.db.models import Count


class CustomQuerySet(QuerySet):
    """Класс типовых запросов."""

    def annotate_comment_count(self):
        """Считает число комментариев к посту."""
        return (self.prefetch_related('comments_for_post')
                .annotate(comment_count=Count('comments_for_post'))
                .order_by('-pub_date', 'title'))

    def publish_filter(self):
        """Запрос опубликованных постов с датой не позднее сейчас."""
        return (self
                .select_related('author', 'category')
                .filter(
                    is_published=True,
                    pub_date__lte=dt.now(),
                ))

    def category_filter(self):
        """Запрос опубликованной категории."""
        return self.publish_filter().filter(category__is_published=True)

    def all_filter(self):
        """Применить все фильтры."""
        return self.category_filter().annotate_comment_count()
