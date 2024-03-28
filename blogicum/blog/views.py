from django.shortcuts import get_object_or_404  # type: ignore
from django.db.models import QuerySet  # type: ignore
from django.views.generic import CreateView  # type: ignore
from django.views.generic import DeleteView, ListView, UpdateView
from django.contrib.auth import get_user_model  # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.urls import reverse  # type: ignore
from django.views.generic.detail import SingleObjectMixin  # type: ignore

from .models import Category, Comment, Post
from .forms import CommentForm, PostForm, ProfileForm
from .mixins import OnlyAuthorMixin


NUM_IN_PAGE: int = 10  # Число новостей на странице.
User = get_user_model()


class IndexListView(ListView):
    """Главная страница."""

    template_name: str = 'blog/index.html'
    paginate_by: int = NUM_IN_PAGE

    def get_queryset(self) -> QuerySet:
        """Возвращает список публикаций."""
        return Post.objects.category_filter()


class PostDetailView(SingleObjectMixin, ListView):
    """
    Отдельный пост.

    В качестве предка выбран ListView, поскольку он предоставляет
    удобные средства для пагинации списка комментариев.
    Согласно stackoverflow, в данном случае выбор между ListView и DetailView
    является преимущественно делом вкуса.
    https://stackoverflow.com/questions/9777121/django-generic-views-when-to-use-listview-vs-detailview
    """

    template_name: str = 'blog/detail.html'
    paginate_by: int = NUM_IN_PAGE
    pk_url_kwarg = 'post_id'

    def get(self, request, *args, **kwargs):
        """Устанавливает объект поста."""
        self.object = self.get_object(
            queryset=Post.objects.annotate_comment_count())
        if self.object.author != self.request.user:
            self.object = self.get_object(
                queryset=Post.objects.category_filter())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст сведения о посте."""
        context: dict = super().get_context_data(**kwargs)
        context['post'] = self.object
        context['comments'] = self.get_queryset()
        if self.request.user.is_authenticated:
            context['form'] = CommentForm(self.request.POST or None)
        return context

    def get_queryset(self) -> QuerySet:
        """Возвращает список комментариев данного поста."""
        queryset: QuerySet = (self.object.
                              comments_for_post.select_related('author'))
        return queryset


class CategoryListView(SingleObjectMixin, ListView):
    """Категория постов."""

    template_name: str = 'blog/category.html'
    paginate_by: int = NUM_IN_PAGE
    slug_url_kwarg = 'category_slug'
    slug_field = 'slug'

    def get(self, request, *args, **kwargs):
        """Устанавливает объект категории."""
        self.object = self.get_object(
            queryset=Category.objects.filter(is_published=True))
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст сведения о категории."""
        context: dict = super().get_context_data(**kwargs)
        context['category'] = self.object
        return context

    def get_queryset(self) -> QuerySet:
        """Возвращает список публикаций данной категории."""
        return self.object.posts_for_category.publish_filter()


class ProfileListView(SingleObjectMixin, ListView):
    """Страница пользователя со списком публикаций."""

    paginate_by: int = NUM_IN_PAGE
    template_name: str = 'blog/profile.html'
    slug_url_kwarg = 'name_slug'
    slug_field = 'username'

    def get(self, request, *args, **kwargs):
        """Устанавливает объект автора."""
        self.object = self.get_object(
            queryset=User.objects.all())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст сведения о профиле пользователя."""
        context: dict = super().get_context_data(**kwargs)
        context['profile'] = self.object
        return context

    def get_queryset(self) -> QuerySet:
        """Возвращает список публикаций данного автора."""
        queryset: QuerySet = (
            Post.objects.
            annotate_comment_count().
            select_related('author', 'category').
            filter(author=self.object))
        if self.request.user != self.object:
            queryset = (
                Post.objects.
                category_filter().
                filter(author=self.object))
        return queryset


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    template_name: str = 'blog/create.html'
    model = Post
    form_class = PostForm

    def get_success_url(self):
        """
        Переадресация.

        В данном случае особое условие, отличающееся
        от перенаправления в модели поста.
        """
        return reverse('blog:profile',
                       kwargs={'name_slug': self.request.user.username})

    def form_valid(self, form):
        """Записать автора."""
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование поста."""

    model = Post
    form_class = PostForm
    template_name: str = 'blog/create.html'
    pk_url_kwarg = 'post_id'


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария."""

    template_name: str = 'blog/detail.html'
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        """
        Записать автора и пост.

        Автор поста может его комментировать всегда,
        а прочие - только если пост прошел проверки.
        """
        post_id = self.kwargs.get('post_id')
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post.objects.annotate_comment_count(),
            pk=post_id)
        if form.instance.post.author != form.instance.author:
            form.instance.post = get_object_or_404(
                Post.objects.category_filter(),
                pk=post_id)
        return super().form_valid(form)


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование комментария."""

    model = Comment
    form_class = CommentForm
    template_name: str = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление поста."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст сведения о форме."""
        context: dict = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=get_object_or_404(
            Post,
            pk=self.kwargs.get(self.pk_url_kwarg)
        ))
        return context

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:profile',
                       kwargs={'name_slug': self.request.user.username})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление комментария."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs.get('post_id')})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    model = User
    form_class = ProfileForm
    template_name: str = 'blog/user.html'

    def get_object(self):
        """Возвращает профиль."""
        self.kwargs['pk'] = self.request.user.pk
        self.pk_url_kwarg = 'pk'
        return super().get_object()

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:profile',
                       kwargs={'name_slug': self.request.user.username})
