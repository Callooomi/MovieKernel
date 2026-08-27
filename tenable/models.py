import re
from django.db import models
from django.utils import timezone


def normalize_text(text):
    """Strip punctuation/spacing for grammar-blind matching (e.g. 'spiderman' == 'Spider-Man')."""
    return re.sub(r"[-'.\s]", "", text or "").lower()


class TenableQuestion(models.Model):
    class QuestionType(models.TextChoices):
        MOVIE = 'movie', 'Movie'
        ACTOR = 'actor', 'Actor'

    question_type = models.CharField(
        max_length=10,
        choices=QuestionType.choices,
        default=QuestionType.MOVIE,
        help_text="Whether the answers to this puzzle are movie titles or actor names — "
                  "controls which autocomplete list players see.",
    )
    question_text = models.CharField(max_length=255)
    description = models.TextField(
        blank=True,
        help_text="Optional note shown under the question — bonus rules, an 'as of' date, etc.",
    )
    release_date = models.DateField(
        default=timezone.localdate,
        help_text="The puzzle goes live on this date. Set a future date to pre-write and schedule it.",
    )

    def __str__(self):
        return self.question_text


class TenableAnswer(models.Model):
    question = models.ForeignKey(TenableQuestion, on_delete=models.CASCADE, related_name='answers')
    answer_text = models.CharField(max_length=255)
    clue = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional hint shown under this answer's number until it's found — "
                  "e.g. the film title, for a 'name the actor' puzzle.",
    )

    def __str__(self):
        return self.answer_text


class MovieTitle(models.Model):
    title = models.CharField(max_length=255)
    normalized_title = models.CharField(max_length=255, blank=True, default='', db_index=True)

    def save(self, *args, **kwargs):
        self.normalized_title = normalize_text(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ActorName(models.Model):
    name = models.CharField(max_length=255)
    normalized_name = models.CharField(max_length=255, blank=True, default='', db_index=True)

    def save(self, *args, **kwargs):
        self.normalized_name = normalize_text(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
