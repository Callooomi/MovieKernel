from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TenableAnswer, MovieTitle


@receiver(post_save, sender=TenableAnswer)
def add_answer_to_movie_titles(sender, instance, **kwargs):
    """Every correct Tenable answer is also added to the MovieTitle autocomplete
    list, so the typed/suggested title always matches the answer exactly."""
    title = (instance.answer_text or '').strip()
    if title:
        MovieTitle.objects.get_or_create(title=title)
