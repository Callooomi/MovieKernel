
from django.db import models
from django.utils import timezone

class Board(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    release_date = models.DateField(
        default=timezone.localdate,
        help_text="The board goes live on this date. Set a future date to pre-make and schedule it.",
    )

    def __str__(self):
        return self.name

class Tile(models.Model):
    TILE_TYPES = [
        ('actor', 'Actor'),
        ('movie', 'Movie'),
    ]

    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='tiles')
    label = models.CharField(max_length=255)
    tile_type = models.CharField(max_length=6, choices=TILE_TYPES)
    column = models.PositiveSmallIntegerField()  # 1 to 5 only

    def __str__(self):
        return f"{self.label} (Col {self.column})"

class Link(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='links')
    from_tile = models.ForeignKey(Tile, on_delete=models.CASCADE, related_name='from_links')
    to_tile = models.ForeignKey(Tile, on_delete=models.CASCADE, related_name='to_links')

    def __str__(self):
        return f"{self.from_tile} → {self.to_tile}"
