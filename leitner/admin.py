from django.contrib import admin
from .models import CustomUser, Language, Box, Card


# Register CustomUser with admin site
@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("email", "name", "is_staff", "is_superuser", "created_at")
    search_fields = ("email", "name")
    list_filter = ("is_staff", "is_superuser")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        (None, {"fields": ("email", "name", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )


# Register Language with admin site
@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_at")
    search_fields = ("name", "code")
    readonly_fields = ("created_at", "updated_at")


# Register Box with admin site
@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "source_language", "target_language", "created_at")
    search_fields = ("name", "description")
    list_filter = ("source_language", "target_language")
    readonly_fields = ("created_at", "updated_at")


# Register Card with admin site
@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ("source_text", "target_text", "box", "recall_count", "next_recall")
    search_fields = ("source_text", "target_text")
    list_filter = ("box", "recall_count")
    readonly_fields = ("created_at", "updated_at", "last_recall")
    fieldsets = (
        (None, {"fields": ("source_text", "target_text", "box")}),
        (
            "Recall Information",
            {"fields": ("recall_count", "last_recall", "next_recall")},
        ),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
