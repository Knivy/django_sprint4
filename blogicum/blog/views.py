from django.shortcuts import get_object_or_404  # type: ignore
from django.db.models import QuerySet  # type: ignore
from django.views.generic import CreateView  # type: ignore
from django.views.generic import DeleteView, ListView, UpdateView
from django.contrib.auth import get_user_model  # type: ignore
from django.contrib.auth.mixins import LoginRequiredMixin  # type: ignore
from django.urls import reverse  # type: ignore

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


class PostDetailView(ListView):
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
    context_object_name = 'comments'

    def get_post(self) -> Post:
        """
        Возвращает пост.

        Поскольку выбран ListView, то get_object относится к комментарию,
        а не посту, поэтому этот метод его не дублирует.
        """
        post_id = self.kwargs.get('post_id')
        if 'post' not in self.__dict__:
            post: Post = get_object_or_404(
                Post.objects.annotate_comment_count(),
                pk=post_id,
            )
            if post.author != self.request.user:
                post = get_object_or_404(
                    Post.objects.category_filter(),
                    pk=post_id,
                )
            self.publication = post
        return self.publication

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст сведения о посте."""
        context: dict = super().get_context_data(**kwargs)
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
    paginate_by: int = NUM_IN_PAGE

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
        context: dict = super().get_context_data(**kwargs)
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

    paginate_by: int = NUM_IN_PAGE
    template_name: str = 'blog/profile.html'

    def get_author(self) -> object:
        """Возвращает автора."""
        if 'author' not in self.__dict__:
            author: object = get_object_or_404(
                User,
                username=self.kwargs.get('name_slug'))
            self.author = author
        return self.author

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст сведения о профиле пользователя."""
        context: dict = super().get_context_data(**kwargs)
        context['profile'] = self.get_author()
        return context

    def get_queryset(self) -> QuerySet:
        """Возвращает список публикаций данного автора."""
        author = self.get_author()
        queryset: QuerySet = (
            Post.objects.
            annotate_comment_count().
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

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs.get('post_id')})

    def form_valid(self, form):
        """Записать автора."""
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post.objects.annotate_comment_count(),
            pk=self.kwargs.get('post_id'))
        return super().form_valid(form)


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    """Редактирование комментария."""

    form_class = CommentForm
    template_name: str = 'blog/comment.html'

    def get_object(self):
        """Возвращает комментарий."""
        return get_object_or_404(Comment,
                                 pk=self.kwargs.get('comment_id'))

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs.get('post_id')})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление поста."""

    template_name = 'blog/create.html'

    def get_object(self):
        """Возвращает пост."""
        return get_object_or_404(Post,
                                 pk=self.kwargs.get('post_id'))

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:profile',
                       kwargs={'name_slug': self.request.user.username})


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    """Удаление комментария."""

    template_name = 'blog/comment.html'

    def get_object(self):
        """Возвращает комментарий."""
        return get_object_or_404(Comment,
                                 pk=self.kwargs.get('comment_id'))

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.kwargs.get('post_id')})


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля."""

    form_class = ProfileForm
    template_name: str = 'blog/user.html'

    def get_object(self):
        """Возвращает профиль."""
        return get_object_or_404(User,
                                 pk=self.request.user.pk)

    def get_success_url(self):
        """Переадресация."""
        return reverse('blog:profile',
                       kwargs={'name_slug': self.request.user.username})
