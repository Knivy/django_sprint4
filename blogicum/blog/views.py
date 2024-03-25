from django.shortcuts import get_object_or_404  # type: ignore
from django.db.models import QuerySet  # type: ignore
from django.views.generic import CreateView  # type: ignore
from django.views.generic import DeleteView, ListView, UpdateView
from django.contrib.auth import get_user_model  # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy  # type: ignore

from .models import Category, Comment, Post
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
        if self.request.user.is_authenticated:
            context['form'] = CommentForm(self.request.POST or None)
        return context

    def get_queryset(self) -> QuerySet:
        """Возвращает список комментариев данного поста."""
        post: Post = self.get_post()
        queryset: QuerySet = post.comments_for_post.select_related('author')
        return queryset


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
        """Переадресация."""
        return reverse_lazy("blog:profile", kwargs={"pk": self.author})

    def form_valid(self, form):
        """Записать автора."""
        form.instance.author = self.request.user
        return super().form_valid(form)


class OnlyAuthorMixin(UserPassesTestMixin):
    """Проверка на авторство."""

    def test_func(self):
        """Проверка на авторство."""
        object = self.get_object()
        return object.author == self.request.user


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostForm
    template_name: str = 'blog/create.html'


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    template_name: str = 'blog/detail.html'
    model = Comment
    form_class = CommentForm

    def get_success_url(self):
        """Переадресация."""
        return reverse_lazy("blog:post_detail",
                            kwargs={"id": self.kwargs.get('post_id')})

    def form_valid(self, form):
        """Записать автора."""
        form.instance.author = self.request.user
        form.instance.post.comment_count += 1
        return super().form_valid(form)


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование комментария."""

    model = Comment
    form_class = CommentForm
    template_name: str = 'blog/comment.html'


class PostDeleteView(DeleteView):
    """Удаление поста."""

    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')


class CommentDeleteView(DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')
