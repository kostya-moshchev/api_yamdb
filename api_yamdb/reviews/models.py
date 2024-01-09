from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import UniqueConstraint


from django.db import models


class Category(models.Model):
    """Категории"""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Genre(models.Model):
    """Жанры"""
    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Произведения"""
    name = models.CharField(max_length=256)
    year = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    genre = models.ManyToManyField(Genre, related_name='titles')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles')

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser):
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    bio = models.TextField(blank=True)
    role = models.CharField(
        max_length=10,
        choices=[("user", "User"), ("moderator", "Moderator"), ("admin", "Admin")],
        default="user",
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.username


class BaseAuthorModel(models.Model):
    """Абстрактная модель.

    Добавляет к модели автора, текст и дату публикации.
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
    score = models.IntegerField(
        validators=[
            MinValueValidator(1, message="Нельзя поствить оценку ниже 1."),
            MaxValueValidator(10, message="Нельзя поставить оценку выше 10."),
        ]
    )

    def __str__(self):
        return self.text[:20]

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        constraints = [
            UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review_per_user_title'
            )
        ]


@receiver(post_save, sender=Review)
@receiver(post_delete, sender=Review)
def update_title_rating(instance, **kwargs):
    title = instance.title
    reviews = title.reviews.all()
    total_score = sum(review.score for review in reviews)
    num_reviews = len(reviews)
    if num_reviews > 0:
        title.rating = round(total_score / num_reviews)
    else:
        title.rating = None

    title.save()


class Comment(BaseAuthorModel):
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

    def __str__(self):
        return self.text[:20]

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
