import re
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Category, Genre, Title
from reviews.models import Comment, Review
from reviews.models import User
from rest_framework.serializers import (
    CharField,
    EmailField,
)


class BaseUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User

    def validate_username(self, value):
        # Проверяем, что значение соответствует регулярному выражению
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError(
                'Недопустимые символы в имени пользователя.')

        # Проверяем, что значение не равно "me"
        if value.lower() == "me":
            raise serializers.ValidationError(
                'Имя пользователя не может быть "me".')

        return value


class UserSerializer(BaseUserSerializer):

    class Meta(BaseUserSerializer.Meta):
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )

    def validate_role(self, value):
        allowed_roles = ['admin', 'moderator', 'user']
        if value not in allowed_roles:
            raise serializers.ValidationError('Недопустимая роль.')

        return value


class UserPatchSerializer(UserSerializer):
    '''
    Этот сериализатор только для запроса http://127.0.0.1:8000/api/v1/users/me/
    Он исключает "role"
    '''

    class Meta(UserSerializer.Meta):
        read_only_fields = ("role",)


class SignUpSerializer(BaseUserSerializer):
    username = CharField(max_length=150, required=True,)
    email = EmailField(max_length=254, required=True,)

    class Meta(BaseUserSerializer.Meta):
        fields = (
            "username",
            "email",
        )

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username=username, email=email).exists():
            return data
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already taken')
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('This username is already taken')
        return data


class TokenSerializer(serializers.Serializer):
    username = CharField(max_length=150, required=True)
    confirmation_code = CharField(required=True)


class BasicSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)


class CategorySerializer(BasicSerializer):

    class Meta(BasicSerializer.Meta):
        model = Category


class GenreSerializer(BasicSerializer):

    class Meta(BasicSerializer.Meta):
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Title


class TitleSerializer(serializers.ModelSerializer):
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug')
    genre = SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug', many=True)

    class Meta:
        fields = '__all__'
        model = Title

    def to_representation(self, instance):
        serializer = TitleReadSerializer(instance)
        return serializer.data


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('title', )


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        fields = '__all__'
        model = Comment
        read_only_fields = ('review', )
