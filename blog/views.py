from django.shortcuts import render, get_object_or_404

from .models import Article


def home(request):
    """Homepage: a featured article on top, then the rest as a stacked feed."""
    published = Article.objects.filter(is_published=True)
    featured = published.first()
    rest = published[1:] if featured else published
    return render(request, 'blog/home.html', {
        'featured': featured,
        'articles': rest,
    })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    return render(request, 'blog/article_detail.html', {'article': article})


def about(request):
    return render(request, 'blog/about.html')
