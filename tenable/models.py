from django.db import models
from django.utils import timezone


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

    def __str__(self):
        return self.answer_text


class MovieTitle(models.Model):
    title = models.CharField(max_length=255)

    def __str__(self):
        return self.title


class ActorName(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name