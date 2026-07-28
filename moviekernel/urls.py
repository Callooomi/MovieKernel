from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def ads_txt(request):
    content = "google.com, pub-1292737363273646, DIRECT, f08c47fec0942fa0\n"
    return HttpResponse(content, content_type="text/plain")


def robots_txt(request):
    content = "User-agent: *\nDisallow: /admin/\n"
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),  # powers the editor's image uploads
    path('ads.txt', ads_txt),
    path('robots.txt', robots_txt),
    # Games
    path('tenable/', include(('tenable.urls', 'tenable'), namespace='tenable')),
    path('bingo/', include(('bingo.urls', 'bingo'), namespace='bingo')),
    path('higherorlower/', include('higherorlower.urls', namespace='higherorlower')),
    path('networks/', include(('networks.urls', 'networks'), namespace='networks')),
    # Quizzes
    path('quizzes/', include(('quizzes.urls', 'quizzes'), namespace='quizzes')),
    # Blog (homepage)
    path('', include('blog.urls')),
]
# Serve media files during development (DEBUG = True)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)