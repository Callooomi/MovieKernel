from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TenableAnswer, MovieTitle, ActorName


@receiver(post_save, sender=TenableAnswer)
def add_answer_to_autocomplete_list(sender, instance, **kwargs):
    """Every correct Tenable answer is also added to the matching autocomplete
    list — MovieTitle or ActorName, depending on the question's type — so the
    typed/suggested value always matches the answer exactly."""
    text = (instance.answer_text or '').strip()
    if not text:
        return

    if instance.question.question_type == instance.question.QuestionType.ACTOR:
        ActorName.objects.get_or_create(name=text)
    else:
        MovieTitle.objects.get_or_create(title=text)