from django.core.management.base import BaseCommand
from tenable.models import MovieTitle
import csv

class Command(BaseCommand):
    help = 'Import movie titles from a CSV file into the MovieTitle model.'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        created_count = 0
        skipped_count = 0

        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row:  # skip empty rows
                    title = row[0].strip()
                    if title:
                        obj, created = MovieTitle.objects.get_or_create(title=title)
                        if created:
                            created_count += 1
                        else:
                            skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"Import complete: {created_count} titles added, {skipped_count} duplicates skipped."
        ))
