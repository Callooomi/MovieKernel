from django import forms
from django.contrib import admin
from .models import Board, Tile, Link

PATH_DELIMITER = '|'
COLUMNS = 5
REQUIRED_PATHS = 6


class BoardAdminForm(forms.ModelForm):
    paths_text = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 10, 'cols': 100}),
        required=False,
        label='Paths (only used when creating a new board)',
        help_text=(
            "Paste all 6 paths here, one per line, with the 5 labels for that path "
            "separated by a pipe ( | ). Each path becomes its own independent chain "
            "of 5 brand-new tiles — nothing is ever shared between paths, even if "
            "the same label appears on two different lines. "
            "Leave this blank when editing an existing board — it only ever runs once, "
            "at creation, and never touches tiles/links that already exist.\n\n"
            "Example line:\n"
            "Tom Hanks | Forrest Gump | Robert Zemeckis | Back to the Future | Michael J. Fox"
        ),
    )

    class Meta:
        model = Board
        fields = ['name', 'release_date']

    def clean_paths_text(self):
        text = self.cleaned_data.get('paths_text', '').strip()
        if not text:
            return []

        lines = [line.strip() for line in text.splitlines() if line.strip()]
        parsed_paths = []
        for line_num, line in enumerate(lines, start=1):
            parts = [p.strip() for p in line.split(PATH_DELIMITER)]
            if len(parts) != COLUMNS:
                raise forms.ValidationError(
                    f"Line {line_num} has {len(parts)} item(s) — needs exactly "
                    f"{COLUMNS}, separated by '{PATH_DELIMITER}'."
                )
            if any(not p for p in parts):
                raise forms.ValidationError(f"Line {line_num} has an empty label.")
            parsed_paths.append(parts)

        if len(parsed_paths) != REQUIRED_PATHS:
            raise forms.ValidationError(
                f"Expected {REQUIRED_PATHS} paths, found {len(parsed_paths)}. "
                "Leave the box empty entirely to skip bulk creation and add tiles "
                "manually below instead."
            )
        return parsed_paths


class TileInline(admin.TabularInline):
    model = Tile
    extra = 0


class LinkInline(admin.TabularInline):
    model = Link
    fk_name = 'board'
    extra = 0


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    form = BoardAdminForm
    inlines = [TileInline, LinkInline]
    list_display = ['name', 'release_date', 'created_at']
    list_filter = ['release_date']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Only ever runs on initial creation — never touches an existing board's
        # tiles/links, even if this field somehow isn't empty on an edit.
        if not change:
            paths = form.cleaned_data.get('paths_text')
            if paths:
                self._build_from_paths(obj, paths)

    def _build_from_paths(self, board, paths):
        for path in paths:
            tiles = [
                Tile.objects.create(
                    board=board,
                    label=label,
                    tile_type='movie',  # not used anywhere in the game; kept only for schema compatibility
                    column=i + 1,
                )
                for i, label in enumerate(path)
            ]
            for i in range(COLUMNS - 1):
                Link.objects.create(
                    board=board,
                    from_tile=tiles[i],
                    to_tile=tiles[i + 1],
                )


admin.site.register(Tile)
admin.site.register(Link)