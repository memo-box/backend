from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This prevents Django from creating a table for BaseModel


class CustomUser(AbstractUser, BaseModel):
    username = None  # Remove username
    last_name = None  # Remove last name
    first_name = None  # Optional, if not needed
    email = models.EmailField(unique=True)  # Use email as a unique identifier
    name = models.CharField(max_length=255)

    USERNAME_FIELD = "email"  # Set email as the unique identifier
    REQUIRED_FIELDS = []  # Remove unnecessary fields

    def __str__(self):
        return self.email


class Language(BaseModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Box(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField()
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    source_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="source_boxes"
    )
    target_language = models.ForeignKey(
        Language, on_delete=models.CASCADE, related_name="target_boxes"
    )

    def __str__(self):
        return self.name


class Card(BaseModel):
    source_text = models.TextField()
    target_text = models.TextField()
    recall_count = models.IntegerField(default=0)
    last_recall = models.DateTimeField(null=True, blank=True)
    next_recall = models.DateTimeField(auto_now_add=True)
    box = models.ForeignKey(Box, on_delete=models.CASCADE)

    def __str__(self):
        return self.source_text
