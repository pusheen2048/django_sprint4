from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView,
                                  DetailView, ListView, UpdateView)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import User, UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Count
from blog.models import Category, Comment, Post
from blog.forms import CommentForm, PostForm, UserUpdateForm


def get_published_posts():
    return (Post.objects.filter(pub_date__lte=timezone.now(),
                                is_published=True,
                                category__is_published=True)
                        .select_related('category', 'author')
                        .annotate(comment_count=Count('comment'))
                        .order_by('-pub_date'))


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_queryset(self):
        return get_published_posts()


class RegistrationView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('blog:index')


class ProfileView(DetailView):
    model = User
    template_name = 'blog/profile.html'

    def get_object(self):
        username = self.kwargs.get('username')
        return get_object_or_404(self.model, username=username)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.object
        context['profile'] = user
        posts = (Post.objects.select_related('category', 'author')
                             .filter(author=user)
                             .annotate(comment_count=Count('comment'))
                             .order_by('-pub_date'))
        if user != self.request.user:
            posts = posts.filter(is_published=True,
                                 pub_date__lte=timezone.now())
        paginator = Paginator(posts, 10)
        page = paginator.get_page(self.request.GET.get('page'))
        context['page_obj'] = page
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserUpdateForm

    def get_object(self):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class ChangePasswordView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/profile.html'

    def form_valid(self, form):
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user
        return context

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        user = self.request.user
        post_id = self.kwargs.get('post_id')
        posts = Post.objects.select_related('category', 'author', 'location')
        if user and user.is_authenticated:
            post = get_object_or_404(posts, pk=post_id)
            if post and post.author == user:
                return post
        return get_object_or_404(posts.filter(is_published=True,
                                              pub_date__lte=timezone.now(),
                                              category__is_published=True),
                                 pk=post_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = self.get_object().comment.select_related('author')
        context['form'] = CommentForm()
        context['comments'] = comments
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:profile',
                            kwargs={'username': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'blog/create.html'
    form_class = PostForm
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/detail.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        if post.author != request.user:
            return redirect('blog:post_detail', post_id=post_id)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm()
        return context


class CategoryPostsView(ListView):
    template_name = 'blog/category.html'
    paginate_by = 10

    def get_queryset(self):
        category = self.kwargs.get('category_slug')
        queryset = get_published_posts()
        return queryset.filter(category__slug=category)

    def get_context_data(self, **kwargs):
        category = self.kwargs.get('category_slug')
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category,
                                                slug=category,
                                                is_published=True)
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def form_valid(self, form):
        post_id = self.kwargs.get('post_id')
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=post_id)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.kwargs.get('post_id')})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    template_name = 'blog/comment.html'
    form_class = CommentForm
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return Comment.objects.filter(author=self.request.user,
                                      post=post)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.object
        return context


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_queryset(self):
        post = get_object_or_404(Post, pk=self.kwargs.get('post_id'))
        return Comment.objects.filter(author=self.request.user, post=post)

    def get_success_url(self):
        return reverse_lazy('blog:post_detail',
                            kwargs={'post_id': self.object.post.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment'] = self.object
