from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from manageBlog.models import Post
from django.views.generic import ListView

class BlogListView(ListView):
    model = Post
    template_name = 'manageBlog/blog.html'
    context_object_name = "posts"
    paginate_by = 3

    def get_context_data(self, **kwargs):
        context = super(BlogListView,self).get_context_data(**kwargs)
        posts = Post.objects.all().order_by("-date")
        paginator = Paginator(posts, self.paginate_by)
        page = self.request.GET.get('page')

        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)

        context['posts'] = posts
        return context
