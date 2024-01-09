from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import ReviewViewSet, CommentViewSet, CategoryViewSet, GenreViewSet, TitleViewSet

v1_router = DefaultRouter()

reviews_url = r"titles/(?P<title_id>\d+)/reviews"
comments_url = rf"{reviews_url}/(?P<review_id>\d+)/comments"

v1_router.register(
    reviews_url, ReviewViewSet, basename='review'
)
v1_router.register(
    comments_url, CommentViewSet, basename='comment'
)
v1_router.register(r'categories', CategoryViewSet)
v1_router.register(r'genres', GenreViewSet)
v1_router.register(r'titles', TitleViewSet)

urlpatterns = [
    path('api/v1/', include(v1_router.urls)),
]

