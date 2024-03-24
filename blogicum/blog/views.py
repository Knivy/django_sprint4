from django.shortcuts import get_object_or_404, redirect  # type: ignore
from django.db.models import QuerySet  # type: ignore
from django.views.generic import CreateView  # type: ignore
from django.views.generic import ListView, UpdateView
from django.contrib.auth import get_user_model  # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy  # type: ignore

from .models import Category, Post
from .forms import CommentForm, PostForm


NUM_ON_MAIN: int = 5  # Число новостей на главной странице.
User = get_user_model()


class IndexListView(ListView):
    """Главная страница."""

    template_name: str = 'blog/index.html'
    paginate_by: int = 10

    def get_queryset(self) -> QuerySet:
        """Возвращает список публикаций."""
        queryset: QuerySet = Post.objects.category_filter()[:NUM_ON_MAIN]
        return queryset


class PostDetailView(ListView):
    """Отдельный пост."""

    template_name: str = 'blog/detail.html'
    paginate_by: int = 10
    context_object_name = 'comments'

    def get_post(self) -> Post:
        """Возвращает пост."""
        if 'post' not in self.__dict__:
            post: Post = get_object_or_404(
                Post.objects.category_filter(),
                pk=self.kwargs.get('id'))
            self.publication = post
        return self.publication

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст сведения о посте."""
        context: dict = super().context_data(**kwargs)
        post: Post = self.get_post()
        context['post'] = post
        context['form'] = CommentForm(self.request.POST or None)
        return context

    def get_queryset(self) -> QuerySet:
        """Возвращает список комментариев данного поста."""
        post: Post = self.get_post()
        queryset: QuerySet = post.comments.select_related('author')
        return queryset
    
    def post(self):
        form = CommentForm(self.request.POST or None)
        if form.is_valid():
            form.save()
        return redirect('blog:post_detail', id=self.pk)


class CategoryListView(ListView):
    """Категория постов."""

    template_name: str = 'blog/category.html'
    paginate_by: int = 10

    def get_category(self) -> Category:
        """Возвращает категорию."""
        if 'category' not in self.__dict__:
            category: Category = get_object_or_404(
                Category,
                is_published=True,
                slug=self.kwargs.get('category_slug'))
            self.category = category
        return self.category

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст сведения о категории."""
        context: dict = super().context_data(**kwargs)
        category: Category = self.get_category()
        context['category'] = category
        return context

    def get_queryset(self) -> QuerySet:
        """Возвращает список публикаций данной категории."""
        category: Category = self.get_category()
        queryset: QuerySet = category.posts_for_category.publish_filter()
        return queryset


class ProfileListView(ListView):
    """Страница пользователя со списком публикаций."""

    paginate_by: int = 10
    template_name: str = 'blog/profile.html'

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст сведения о профиле пользователя."""
        context: dict = super().context_data(**kwargs)
        context['profile'] = User.objects.filter(pk=self.kwargs.get('pk'))
        return context

    def get_queryset(self) -> QuerySet:
        """Возвращает список публикаций данного автора."""
        author = User.objects.filter(
            pk=self.kwargs.get('pk'))
        queryset: QuerySet = (
            Post.objects.
            select_related('author', 'category').
            filter(author=author))
        if self.request.user != author:
            queryset = queryset.category_filter()
        return queryset


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    template_name: str = 'blog/create.html'
    model = Post
    form_class = PostForm

    def get_success_url(self):
        return reverse_lazy("blog:profile", kwargs={"pk": self.author})


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверка на авторство."""

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostForm
    template_name: str = 'blog/create.html'
