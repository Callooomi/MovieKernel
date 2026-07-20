### networks/admin.py

from django.contrib import admin
from .models import Board, Tile, Link

class TileInline(admin.TabularInline):
    model = Tile
    extra = 0

class LinkInline(admin.TabularInline):
    model = Link
    fk_name = 'board'
    extra = 0

@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    inlines = [TileInline, LinkInline]
    list_display = ['name', 'release_date', 'created_at']
    list_filter = ['release_date']

admin.site.register(Tile)
admin.site.register(Link)
