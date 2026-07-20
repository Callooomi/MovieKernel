from django.contrib import admin
from .models import BingoPlaceholder, Actor

@admin.register(BingoPlaceholder)
class BingoPlaceholderAdmin(admin.ModelAdmin):
    list_display = ('text', 'image')  # Show the image field in the admin list
    search_fields = ('text',)

class ActorAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('placeholders',)  # Better UI for ManyToMany

admin.site.register(Actor, ActorAdmin)
