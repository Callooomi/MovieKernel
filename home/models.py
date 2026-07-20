from django.db import models
from django.urls import reverse
from django.apps import apps

class GameEntry(models.Model):
    LINK_STATIC = 'static'
    LINK_DYNAMIC = 'dynamic_latest'
    LINK_CHOICES = [
        (LINK_STATIC, 'Static URL'),
        (LINK_DYNAMIC, 'Dynamic — link to latest'),
    ]

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, help_text="For your own reference/admin; not used in routing.")
    image = models.ImageField(upload_to='games/', blank=True, null=True)

    link_type = models.CharField(max_length=20, choices=LINK_CHOICES, default=LINK_STATIC)

    # Static link
    static_url = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="Example: /bingo/ or /higherorlower/"
    )

    # Dynamic latest config
    dynamic_url_name = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="Django URL pattern name that expects a numeric kwarg. Example: 'tenable:play'"
    )
    dynamic_param_name = models.CharField(
        max_length=50, blank=True, null=True,
        help_text="The kwarg name for the URL (e.g., 'question_id', 'game_id', or 'pk')."
    )
    latest_model_label = models.CharField(
        max_length=100, blank=True, null=True,
        help_text="app_label.ModelName to query for latest, e.g. 'tenable.TenableQuestion'"
    )
    latest_field_name = models.CharField(
        max_length=50, default='id',
        help_text="Field used to determine latest (usually 'id')."
    )

    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name

    def resolve_url(self):
        """
        Returns (url, available) where:
        - url is the string to link to
        - available indicates if the target exists (for dynamic mode)
        """
        if self.link_type == self.LINK_STATIC:
            return (self.static_url or '#', bool(self.static_url and self.is_active))

        # Dynamic latest
        try:
            model = apps.get_model(self.latest_model_label)
        except Exception:
            return ('#', False)

        qs = model.objects.all()
        if not qs.exists():
            return ('#', False)

        # Find latest by field (default id)
        latest_obj = qs.order_by(f'-{self.latest_field_name}').first()
        if not latest_obj:
            return ('#', False)

        if not self.dynamic_url_name or not self.dynamic_param_name:
            return ('#', False)

        try:
            url = reverse(self.dynamic_url_name, kwargs={self.dynamic_param_name: getattr(latest_obj, self.latest_field_name)})
            return (url, True)
        except Exception:
            return ('#', False)

    def get_absolute_url(self):
        url, _ = self.resolve_url()
        return url
