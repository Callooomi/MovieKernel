from django.db import models

class BingoPlaceholder(models.Model):
    text = models.CharField(max_length=255)
    image = models.ImageField(upload_to='bingo_images/', null=True, blank=True)  # New image field

    def __str__(self):
        return self.text

class Actor(models.Model):
    name = models.CharField(max_length=255)
    placeholders = models.ManyToManyField(BingoPlaceholder, related_name='actors')

    def __str__(self):
        return self.name
