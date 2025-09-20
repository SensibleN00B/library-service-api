from django.db import models
from django.db.models import Q


class Book(models.Model):

    class CoversStatus(models.TextChoices):
        HARD = "hard", "Hard"
        SOFT = "soft", "Soft"

    title = models.CharField(max_length=64, null=False)
    author = models.CharField(max_length=64, null=False)
    cover = models.CharField(
        max_length=8, choices=CoversStatus.choices, default=CoversStatus.HARD
    )
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=8, decimal_places=2)

    class Meta:
        ordering = ["title", "author"]
        constraints = [
            models.CheckConstraint(
                check=Q(daily_fee__gt=0), name="The value cannot be negative"
            ),
        ]

    def __str__(self):
        return f"{self.title} by {self.author}"
