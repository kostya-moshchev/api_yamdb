from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, filters, status
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import Review, Title, Category, Genre, User
from .serializers import (
    CategorySerializer, GenreSerializer, TitleSerializer,
    TitleReadSerializer, ReviewSerializer, CommentSerializer,
    UserSerializer, SignUpSerializer, TokenSerializer,
    UserPatchSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdmin, IsAdminOrReadOnly
from .filters import TitleFilter
from .pagination import PagePagination
from .utils import generate_confirmation_code


class UserViewSet(viewsets.ModelViewSet):
    http_method_names = ("get", "post", "patch", "delete")
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin, ]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    lookup_field = "username"
    filterset_fields = ['username']
    search_fields = ['username']

    @action(detail=False, methods=["get"],
            permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data)

    @me.mapping.patch
    def patch_me(self, request):
        user = request.user
        serializer = UserPatchSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)       


class AuthViewSet(APIView):
    def post(self, request, *args, **kwargs):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user, _ = User.objects.get_or_create(**serializer.validated_data)
        confirmation_code = generate_confirmation_code()
        user.confirmation_code = default_token_generator.make_token(user)
        user.save()
        send_mail(
            'Код подтверждения',
            f'Ваш код подтверждения: {confirmation_code}',
            settings.EMAIL_API_NO_REPLY,
            [user.email],
            fail_silently=False,
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class TokenView(APIView):
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User, username=serializer.validated_data['username'])
        if not default_token_generator.check_token(
            user,
            request.data.get('confirmation_code')
        ):
            return Response(
                'Вы ошиблись в поле toden или username',
                status=status.HTTP_400_BAD_REQUEST
            )
        access = AccessToken.for_user(user)
        token = {
            'access': str(access),
        }
        return Response(token, status=status.HTTP_200_OK)


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class BasicViewSet(CreateListDestroyViewSet):
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PagePagination


class CategoryViewSet(BasicViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BasicViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')).order_by('name')
    permission_classes = [IsAdminOrReadOnly, ]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter
    pagination_class = PagePagination
    http_method_names = ("get", "post", "delete", "patch")

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return TitleReadSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ("get", "post", "delete", "patch")

    def get_title(self):
        title_id = self.kwargs['title_id']
        return get_object_or_404(Title, id=title_id)

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        title = self.get_title()
        existing_review = Review.objects.filter(
            author=self.request.user, title=title)

        if existing_review.exists():
            raise ValidationError(
                'Вы уже оставили отзыв на это произведение.')
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ("get", "post", "delete", "patch")

    def get_title(self):
        title_id = self.kwargs['title_id']
        return get_object_or_404(Title, id=title_id)

    def get_review(self):
        review_id = self.kwargs['review_id']
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        if self.get_review().title != self.get_title():
            raise ValidationError('Ошибка в urls')
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
