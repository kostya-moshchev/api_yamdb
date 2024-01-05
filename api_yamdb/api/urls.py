from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import ReviewViewSet, CommentViewSet


v1_router = DefaultRouter()

v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewViewSet, basename='review'
)
v1_router.register(
    r'(?P<review_id>\d+)/comments', CommentViewSet, basename='comment'
)

urlpatterns = [
    path('api/v1/', include(v1_router.urls)),
]
