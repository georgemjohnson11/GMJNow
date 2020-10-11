from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=30)
    bodytext = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    tags = ArrayField(models.CharField(max_length=30), default=None, null=True, blank=True)
    comments = models.ManyToManyField('Comment', default=None, blank=True)

    def __str__(self):
        return self.title


class Comment(models.Model):
    blog_post = models.ForeignKey(Post, on_delete=models.CASCADE)
    headline = models.CharField(max_length=255)
    body_text = models.TextField()
    pub_date = models.DateField()
    mod_date = models.DateField()
    author = models.ManyToManyField('Author')
    n_comments = models.IntegerField()
    n_pingbacks = models.IntegerField()
    rating = models.IntegerField()

    def __str__(self):
        return self.headline

class Author(models.Model):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)

    def __str__(self):
        return self.name