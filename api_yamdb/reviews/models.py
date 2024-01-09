from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import UniqueConstraint


User = get_user_model()


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
