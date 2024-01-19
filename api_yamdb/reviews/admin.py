from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from reviews.models import User, Category, Genre, Review, Title

admin.site.register(User, UserAdmin)
admin.site.register(Category)
admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(Title)
