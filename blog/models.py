from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from markdownx.models import MarkdownxField
from markdownx.utils import markdownify


class Article(models.Model):
    """A single blog post / data-analysis article.

    The body is written in Markdown in the admin. Because the body may contain
    raw HTML (e.g. a pasted-in interactive chart embed), it is rendered with
    |safe in the template and is therefore trusted: only you, via the admin,
    can create it.
    """

    title = models.CharField(max_length=200)
    slug = models.SlugField(
        max_length=220, unique=True, blank=True,
        help_text="Leave blank to auto-generate from the title.",
    )
    headline = models.CharField(
        max_length=300, blank=True,
        help_text="Short teaser shown under the title on the homepage feed.",
    )
    tag = models.CharField(
        max_length=60, blank=True,
        help_text="Optional category chip, e.g. 'Box office' or 'Genres'.",
    )
    hero_image = models.ImageField(
        upload_to='articles/heroes/', blank=True, null=True,
        help_text="Large image shown on the feed card and at the top of the article.",
    )
    body = MarkdownxField(
        help_text="Write in Markdown. Drag an image straight into the box to upload it.",
    )

    is_published = models.BooleanField(
        default=False,
        help_text="Untick to keep this as a draft (hidden from the site).",
    )
    published_at = models.DateTimeField(
        default=timezone.now,
        help_text="Articles are ordered newest-first by this date.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:200] or 'article'
            slug = base
            n = 2
            while Article.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f'{base}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'slug': self.slug})

    @property
    def body_html(self):
        """Markdown rendered to HTML, using the extensions set in settings."""
        return markdownify(self.body)
