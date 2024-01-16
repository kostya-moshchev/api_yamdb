from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import UniqueConstraint


class Category(models.Model):
    """Категории"""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        default_related_name = "categories"


class Genre(models.Model):
    """Жанры"""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"
        default_related_name = "genres"


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        verbose_name="Название",
        max_length=256,
        db_index=True,
    )
    year = models.PositiveSmallIntegerField(
        verbose_name="Год создания",
        db_index=True,
    )
    description = models.TextField(
        verbose_name="Описание",
        blank=True,
    )
    genre = models.ManyToManyField(
        Genre, through='GenreTitle', related_name='titles', blank=True)
    category = models.ForeignKey(
        Category,
        verbose_name="Категория",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="titles",
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.genre} {self.title}"


class UserManager(BaseUserManager):

    def create_user(self, email, username,
                    role, password=None, **extra_fields):
        user = self.model(
            email=self.normalize_email(email),
            username=username, role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
            self, email, username, role, password=None, **extra_fields):
        user = self.create_user(
            email=email,
            username=username,
            role='admin',
            **extra_fields,
        )
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=10,
        choices=[
            ("user", "User"),
            ("moderator", "Moderator"),
            ("admin", "Admin")
        ],
        default="user"
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'

    def __str__(self):
        return self.username

    class Meta:
        ordering = ("username",)


class BaseAuthorModel(models.Model):
    """
    Абстрактная модель.
    Добавляет к модели автора, текст и дату публикации
    """
    text = models.TextField(
        verbose_name="Текст",
    )
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text


class Review(BaseAuthorModel):
    """Модель отзывов на произведения"""
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    title = models.ForeignKey(
        Title,
        verbose_name="Произведение",
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1, message="Нельзя поствить оценку ниже 1."),
            MaxValueValidator(10, message="Нельзя поставить оценку выше 10."),
        ]
    )

    class Meta(BaseAuthorModel.Meta):
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review_per_user_title'
            )
        ]

    def __str__(self):
        return self.text[:20]


class Comment(BaseAuthorModel):
    """Модель комментариев"""
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        verbose_name="Отзыв",
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta(BaseAuthorModel.Meta):
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return self.text[:20]
