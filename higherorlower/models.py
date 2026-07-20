# app/models.py
from django.db import models

class Actor(models.Model):
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    box_office = models.PositiveBigIntegerField()
    leading_roles = models.PositiveIntegerField()  # renamed from acting_credits
    oscar_nominations = models.PositiveIntegerField()
    image = models.ImageField(upload_to='actors/', blank=True, null=True)
    image_attribution = models.CharField(
        max_length=200, blank=True, null=True,
        help_text="Photo credit (e.g., 'Photo by John Smith on Unsplash')"
    )

    def __str__(self):
        return self.name
