from django.urls import path, include
from rest_framework import routers

from api.views import CategoryViewSet, GenreViewSet, TitleViewSet


router = routers.DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)
