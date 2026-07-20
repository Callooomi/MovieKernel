from django.shortcuts import render, get_object_or_404
from .models import Quiz


def home(request):
    """Quizzes feed: a featured quiz on top, then the rest as a stacked feed —
    mirrors the blog homepage layout."""
    published = Quiz.objects.filter(is_published=True)
    featured = published.first()
    rest = published[1:] if featured else published
    return render(request, 'quizzes/home.html', {
        'featured': featured,
        'quizzes': rest,
    })


def detail(request, slug):
    quiz = get_object_or_404(Quiz, slug=slug, is_published=True)
    questions = quiz.questions.all()
    return render(request, 'quizzes/detail.html', {
        'quiz': quiz,
        'questions': questions,
        'total': questions.count(),
    })
