from django.contrib import admin
from .models import Quiz, Question


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ('order', 'text', 'image', 'options', 'correct_option', 'reveal_answer')


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'quiz_type', 'is_published', 'published_at')
    list_filter = ('quiz_type', 'is_published')
    search_fields = ('title', 'headline', 'tag')
    inlines = [QuestionInline]
    fields = ('title', 'slug', 'tag', 'headline', 'quiz_type',
              'hero_image', 'is_published', 'published_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'quiz', 'order')
    list_filter = ('quiz',)
    search_fields = ('text',)
    fields = ('quiz', 'order', 'text', 'image', 'options', 'correct_option', 'reveal_answer')
