from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin

from .models import Article


@admin.register(Article)
class ArticleAdmin(MarkdownxModelAdmin):
    list_display = ('title', 'tag', 'is_published', 'published_at')
    list_filter = ('is_published', 'tag')
    list_editable = ('is_published',)
    search_fields = ('title', 'headline', 'body')
    date_hierarchy = 'published_at'
    prepopulated_fields = {'slug': ('title',)}

    fieldsets = (
        ('Article', {
            'fields': ('title', 'slug', 'tag', 'headline', 'hero_image', 'body'),
        }),
        ('Publishing', {
            'fields': ('is_published', 'published_at'),
        }),
    )
