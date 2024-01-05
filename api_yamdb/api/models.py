from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import UniqueConstraint


User = get_user_model()


class Review(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)
    score = models.IntegerField()

    def __str__(self):
        return self.text[:20]

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review_per_user_title'
            )
        ]


@receiver(post_save, sender=Review)
def update_title_rating(instance):
    title = instance.title
    reviews = title.reviews.all()
    total_score = sum(review.score for review in reviews)
    num_reviews = len(reviews)
    if num_reviews > 0:
        title.rating = round(total_score / num_reviews)
    else:
        title.rating = None

    title.save()


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    pub_date = models.DateTimeField(
        'Дата добавления', auto_now_add=True)

    def __str__(self):
        return self.text[:20]
