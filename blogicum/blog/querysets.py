from datetime import datetime as dt  # type: ignore[import-untyped]

from django.db.models import QuerySet  # type: ignore[import-untyped]


class CustomQuerySet(QuerySet):
    """Класс типовых запросов."""

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
