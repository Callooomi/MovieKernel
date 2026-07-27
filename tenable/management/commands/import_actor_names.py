import csv

from django.core.management.base import BaseCommand, CommandError

from tenable.models import ActorName


class Command(BaseCommand):
    help = "Bulk-import actor names from a CSV (reads the 'name' column by default) into the ActorName autocomplete list."

    def add_arguments(self, parser):
        parser.add_argument('csv_path', type=str)
        parser.add_argument(
            '--column', type=str, default='name',
            help="Name of the column containing actor names, if it isn't 'name'.",
        )

    def handle(self, *args, **options):
        csv_path = options['csv_path']
        column = options['column']

        try:
            f = open(csv_path, newline='', encoding='utf-8-sig')
        except OSError as e:
            raise CommandError(f"Couldn't open {csv_path}: {e}")

        with f:
            reader = csv.DictReader(f)
            if column not in (reader.fieldnames or []):
                raise CommandError(
                    f"Column '{column}' not found. Columns in this file: {reader.fieldnames}"
                )

            created = 0
            skipped = 0
            for row in reader:
                name = (row.get(column) or '').strip()
                if not name:
                    skipped += 1
                    continue
                _, was_created = ActorName.objects.get_or_create(name=name)
                if was_created:
                    created += 1
                else:
                    skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Done. Added {created} new actor name(s), skipped {skipped} (blank or already present)."
        ))