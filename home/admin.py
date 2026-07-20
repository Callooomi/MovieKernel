from django.contrib import admin
from .models import GameEntry

@admin.register(GameEntry)
class GameEntryAdmin(admin.ModelAdmin):
    list_display = ('name', 'link_type', 'is_active', 'display_order', 'resolved_link', 'available')
    list_editable = ('is_active', 'display_order')
    list_filter = ('link_type', 'is_active')
    search_fields = ('name', 'slug', 'static_url', 'dynamic_url_name', 'latest_model_label')

    fieldsets = (
        ('Basics', {
            'fields': ('name', 'slug', 'image', 'is_active', 'display_order')
        }),
        ('Link Type', {
            'fields': ('link_type',)
        }),
        ('Static URL', {
            'fields': ('static_url',),
            'description': "Used when link type is 'Static URL'."
        }),
        ('Dynamic Latest', {
            'fields': ('dynamic_url_name', 'dynamic_param_name', 'latest_model_label', 'latest_field_name'),
            'description': "Used when link type is 'Dynamic — link to latest'."
        }),
    )

    def resolved_link(self, obj):
        url, _ = obj.resolve_url()
        return url
    resolved_link.short_description = "Resolved URL"

    def available(self, obj):
        _, ok = obj.resolve_url()
        return ok
    available.boolean = True
    available.short_description = "Available?"
