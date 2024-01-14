from rest_framework.routers import DefaultRouter
from django.urls import include, path

from .views import (
    UserViewSet, ReviewViewSet, CommentViewSet,
    CategoryViewSet, GenreViewSet, TitleViewSet,
    AuthViewSet, TokenView
)

app_name = 'api'

v1_router = DefaultRouter()

reviews_url = r"titles/(?P<title_id>\d+)/reviews"
comments_url = rf"{reviews_url}/(?P<review_id>\d+)/comments"

v1_router.register(
    reviews_url, ReviewViewSet, basename='review'
)
v1_router.register(
    comments_url, CommentViewSet, basename='comment'
)
v1_router.register(r'users', UserViewSet)
v1_router.register(r'categories', CategoryViewSet)
v1_router.register(r'genres', GenreViewSet)
v1_router.register(r'titles', TitleViewSet)
urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/auth/token/', TokenView.as_view()),
    path('v1/auth/signup/', AuthViewSet.as_view()),
]
