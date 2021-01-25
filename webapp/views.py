from django.shortcuts import render

from posts.models import Post

def home(request):
    context = {
        'posts': Post.objects.all()
    }
    return render(request, 'webapp/home.html', context)