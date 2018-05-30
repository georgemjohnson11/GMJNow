from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from manageBlog.models import Post
from django.views.generic import ListView
# Create your views here.

def blogindex(request):
    post_list = Post.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(post_list, 5)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'manageBlog/blog.html', {'posts': posts})

def blogView(request):
    queryset_list = Post.objects.all().order_by("-date")
    paginator = Paginator(queryset_list, 5)
    page_request_var = "page"
    page = request.GET.get(page_request_var)
    try:
        queryset = paginator.page(page)
    except PageNotAnInteger:
        queryset = paginator.page(1)
    except EmptyPage:
        queryset = paginator.page(paginator.num_pages)
    context = {
        "object_list": queryset,
        "page": page
    }
    return render(request, 'manageBlog/blog.html', context)
