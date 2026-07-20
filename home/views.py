from django.shortcuts import render
from .models import GameEntry

def home(request):
    games = GameEntry.objects.filter(is_active=True).order_by('display_order', 'name')

    # Pre-resolve URLs so the template stays simple
    resolved = []
    for g in games:
        url, ok = g.resolve_url()
        resolved.append({
            'obj': g,
            'url': url,
            'available': ok,
        })

    return render(request, 'home/home.html', {'games': resolved})
