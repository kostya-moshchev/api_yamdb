from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Category, Genre, Title
from reviews.models import Comment, Review
from reviews.models import User
from django.contrib.auth import authenticate
from rest_framework.serializers import (
    CharField,
    EmailField,
)


class UserSerializer(serializers.ModelSerializer):
    def validate_username(self, value):
        import re
        # Проверяем, что значение соответствует регулярному выражению
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError('Недопустимые символы в имени пользователя.')

        # Проверяем, что значение не равно "me"
        if value.lower() == "me":
            raise serializers.ValidationError('Имя пользователя не может быть "me".')

        return value

    def validate_role(self, value):
        allowed_roles = ['admin', 'moderator', 'user']
        if value not in allowed_roles:
            raise serializers.ValidationError('Недопустимая роль. Роли должны быть одной из: {}'.format(', '.join(allowed_roles)))

        return value

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )


class UserSerializer1(serializers.ModelSerializer):
    '''
    Этот сериализатор только для запроса http://127.0.0.1:8000/api/v1/users/me/
    Он исключает "role"
    '''
    def validate_username(self, value):
        import re
        # Проверяем, что значение соответствует регулярному выражению
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError('Недопустимые символы в имени пользователя.')

        # Проверяем, что значение не равно "me"
        if value.lower() == "me":
            raise serializers.ValidationError('Имя пользователя не может быть "me".')

        return value

    def validate_role(self, value):
        # Проверяем, что роль существует в допустимых значениях
        allowed_roles = ['admin', 'moderator', 'user']  # Замените этот список на ваши допустимые роли
        if value not in allowed_roles:
            raise serializers.ValidationError('Недопустимая роль. Роли должны быть одной из: {}'.format(', '.join(allowed_roles)))

        return value

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "bio",
            "role",
        )
        read_only_fields = ("role",)


class SignUpSerializer(serializers.ModelSerializer):
    username = CharField(max_length=150, required=True,)
    email = EmailField(max_length=254, required=True,)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
        )

    def validate(self, data):
        # print(value)
        username = data.get('username')
        email = data.get('email')
        if User.objects.filter(username=username, email=email).exists():
            return data
        elif User.objects.filter(email=email).exists():
            raise serializers.ValidationError('This email is already taken')
        elif User.objects.filter(username=username).exists():
            raise serializers.ValidationError('This username is already taken')
        else:
            return data

    def validate_username(self, value):

        import re
        # Проверяем, что значение соответствует регулярному выражению
        if not re.match(r'^[\w.@+-]+\Z', value):
            raise serializers.ValidationError('Недопустимые символы в имени пользователя.')

        # Проверяем, что значение не равно "me"
        if value.lower() == "me":
            raise serializers.ValidationError('Имя пользователя не может быть "me".')

        return value


class TokenSerializer(serializers.Serializer):
    username = CharField(max_length=150, required=True)
    confirmation_code = CharField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
        model = Category


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        exclude = ('id',)
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


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        author = data.get('author')
        title = data.get('title')

        if Review.objects.filter(author=author, title=title).exists():
            raise serializers.ValidationError("This review already exists.")
        return data

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
