from django.core.management.base import BaseCommand
from tenable.models import TenableAnswer, MovieTitle


class Command(BaseCommand):
    help = "Ensure every Tenable correct answer also exists in the MovieTitle autocomplete list."

    def handle(self, *args, **options):
        added = 0
        for ans in TenableAnswer.objects.all():
            title = (ans.answer_text or '').strip()
            if title:
                _, created = MovieTitle.objects.get_or_create(title=title)
                if created:
                    added += 1
        self.stdout.write(self.style.SUCCESS(
            f"Synced answers -> autocomplete list: {added} new title(s) added."
        ))
