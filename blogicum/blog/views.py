from django.shortcuts import get_object_or_404, render
from blog.models import Category, Post
from datetime import datetime


def index(request):
    template = 'blog/index.html'
    context = {'post_list': (Post.objects
                             .filter(is_published=True,
                                     category__is_published=True,
                                     pub_date__lt=datetime.now())
                             .select_related('category'))[:5]}
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'blog/detail.html'
    post = (get_object_or_404(Post.objects.select_related('category'),
                              pk=post_id,
                              is_published=True,
                              category__is_published=True,
                              pub_date__lt=datetime.now()))
    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(Category.objects.values('title',
                                                         'description'),
                                 slug=category_slug,
                                 is_published=True)
    context = {'post_list': (Post.objects
                             .filter(category__slug=category_slug,
                                     pub_date__lt=datetime.now(),
                                     is_published=True)
                             .select_related('category')),
               'category': category}
    return render(request, template, context)
