from django.db.models import Avg
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.template.loader import render_to_string
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, filters, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import SAFE_METHODS
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token

from reviews.models import Review, Title, Category, Genre, User
from .serializers import (CategorySerializer, GenreSerializer,
                          TitleSerializer, TitleReadSerializer,
                          ReviewSerializer, CommentSerializer,
                          UserSerializer, SignUpSerializer,
                          TokenSerializer)
from .permissions import IsAdminUserOrReadOnly, IsOwnerOrReadOnly
from .filters import TitleFilter
from .pagination import PagePagination
from .utils import generate_confirmation_code


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUserOrReadOnly, ]


class AuthViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all
    serializer_class = SignUpSerializer
    permission_classes = [IsAdminUserOrReadOnly, ]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perfom_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perfom_create(self, serializer):
        super().perfom_create(serializer)
        user = User.objects.get(username=self.request.data.get('username'))
        try:
            code = generate_confirmation_code()  # функция генерации кода подтверждения
            send_mail(
                'Код подтверждения',
                f'Ваш код подтверждения: {code}',
                'noreply@yamdb.com',
                [user.email],
                fail_silently=False,
            )
        except ValueError:
            raise ValueError('')



class TokenView(APIView):
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']

        # Generate JWT token for user
        refresh = RefreshToken.for_user(user)
        token = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

        return Response(token, status=status.HTTP_200_OK)


class CreateListDestroyViewSet(mixins.CreateModelMixin,
                               mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               viewsets.GenericViewSet):
    pass


class CategoryViewSet(CreateListDestroyViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PagePagination


class GenreViewSet(CreateListDestroyViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAdminUserOrReadOnly, ]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = PagePagination


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    permission_classes = [IsAdminUserOrReadOnly, ]
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
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerOrReadOnly]
    http_method_names = ("get", "post", "delete", "patch")

    def get_review(self):
        review_id = self.kwargs['review_id']
        return get_object_or_404(Review, id=review_id)

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
