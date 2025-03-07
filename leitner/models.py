from django.contrib.auth.models import AbstractUser, Group, Permission, BaseUserManager
from django.db import models


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This prevents Django from creating a table for BaseModel


class CustomUserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    def _create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('name', 'Admin')  # Default name for superuser

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, BaseModel):
    username = None  # Remove username
    last_name = None  # Remove last name
    first_name = None  # Optional, if not needed
    email = models.EmailField(unique=True)  # Use email as a unique identifier
    name = models.CharField(max_length=255)
    
    # Override the groups field to add related_name
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='customuser_set',
        related_query_name='user'
    )
    
    # Override the user_permissions field to add related_name
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='customuser_set',
        related_query_name='user'
    )

    USERNAME_FIELD = "email"  # Set email as the unique identifier
    REQUIRED_FIELDS = []  # Remove unnecessary fields
    
    objects = CustomUserManager()  # Use the custom manager

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
