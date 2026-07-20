from django.contrib import admin
from .models import TenableQuestion, TenableAnswer, MovieTitle

class TenableAnswerInline(admin.TabularInline):
    model = TenableAnswer
    extra = 10

class TenableQuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'release_date')
    list_filter = ('release_date',)
    search_fields = ('question_text', 'description')
    fields = ('question_text', 'description', 'release_date')
    inlines = [TenableAnswerInline]

    class Media:
        js = ('admin/autocomplete_off.js',)

@admin.register(MovieTitle)
class MovieTitleAdmin(admin.ModelAdmin):
    search_fields = ['title']

admin.site.register(TenableQuestion, TenableQuestionAdmin)
