from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"languages", views.LanguageViewSet)
router.register(r"boxes", views.BoxViewSet)
router.register(r"cards", views.CardViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path("", include(router.urls)),
]
