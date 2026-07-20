import csv

from django.core.management.base import BaseCommand, CommandError
from tenable.models import MovieTitle


class Command(BaseCommand):
    help = (
        "Import movie titles from a CSV that has a header like 'MovieID,Title' "
        "into the MovieTitle autocomplete list. Reads the title column (not the id), "
        "skips the header, copes with commas inside titles and common encodings."
    )

    def add_arguments(self, parser):
        parser.add_argument('csv_file', help="Path to the CSV file.")
        parser.add_argument(
            '--column', default='Title',
            help="Header name of the title column (default: Title).",
        )
        parser.add_argument(
            '--encoding', default=None,
            help="Force a file encoding. If omitted, tries utf-8-sig, utf-8, then latin-1.",
        )

    def _read_rows(self, path, encoding):
        encodings = [encoding] if encoding else ['utf-8-sig', 'utf-8', 'latin-1']
        last_err = None
        for enc in encodings:
            try:
                with open(path, newline='', encoding=enc) as f:
                    return list(csv.reader(f)), enc
            except UnicodeDecodeError as e:
                last_err = e
        raise CommandError(f"Couldn't decode {path}. Last error: {last_err}")

    def handle(self, *args, **opts):
        path = opts['csv_file']
        col = opts['column']

        try:
            rows, enc = self._read_rows(path, opts['encoding'])
        except FileNotFoundError:
            raise CommandError(f"File not found: {path}")

        rows = [r for r in rows if r]  # drop blank lines
        if not rows:
            raise CommandError("CSV appears to be empty.")

        header = [c.strip() for c in rows[0]]
        lowered = [h.lower() for h in header]

        if col.lower() in lowered:
            idx = lowered.index(col.lower())
            data = rows[1:]
            title_is_last = (idx == len(header) - 1)
        else:
            # No matching header — assume there's no header and the title is the
            # last column on each line.
            idx = len(header) - 1
            data = rows
            title_is_last = True
            self.stdout.write(self.style.WARNING(
                f"No '{col}' column found in the header; using the last column instead."
            ))

        added = 0
        skipped = 0
        for row in data:
            if len(row) <= idx:
                continue
            # If the title is the final column, re-join any extra fields so titles
            # containing commas (e.g. 'Lord of the Rings, The') survive intact.
            raw = ','.join(row[idx:]) if title_is_last else row[idx]
            title = raw.strip().strip('"').strip()
            if not title or title.lower() == col.lower():
                continue
            _, created = MovieTitle.objects.get_or_create(title=title)
            if created:
                added += 1
            else:
                skipped += 1

        self.stdout.write(self.style.SUCCESS(
            f"Read {path} (encoding: {enc}). Added {added} new title(s); "
            f"{skipped} already in the list."
        ))
