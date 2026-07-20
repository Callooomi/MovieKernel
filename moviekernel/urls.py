from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),  # powers the editor's image uploads

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
