from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.contrib import admin
from django.utils import timezone
# Create your models here.


class UserProfile(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    isProfessional = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)


class Categories(models.Model):
    name = models.CharField(max_length=200, unique=True)
    _id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return self.name


class Professional(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    location = models.CharField(max_length=200, null=True, blank=True)

    category = models.ForeignKey(
        Categories, on_delete=models.SET_NULL, null=True)
    description = models.TextField(null=True, blank=True)
    # rating = models.DecimalField(
    #     max_digits=7, decimal_places=2, null=True, blank=True)
    # numReviews = models.IntegerField(null=True, blank=True, default=0)
    createdAt = models.DateTimeField(auto_now_add=True)
    _id = models.AutoField(primary_key=True, editable=False)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Review(models.Model):
    professional = models.ForeignKey(
        Professional, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # name = models.CharField(max_length=200, null=True, blank=True)
    rating = models.IntegerField(null=True, blank=True, default=0)
    comment = models.TextField(null=True, blank=True)
    _id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return str(self.rating)


# class Book(models.Model):
#     user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
#     paymentMethod = models.CharField(max_length=200, null=True, blank=True)
#     totalPrice = models.DecimalField(
#         max_digits=7, decimal_places=2, null=True, blank=True)
#     isPaid = models.BooleanField(default=False)
#     paidAt = models.DateTimeField(auto_now_add=False, null=True, blank=True)
#     isCompleted = models.BooleanField(default=False)
#     completedAt = models.DateTimeField(
#         auto_now_add=False, null=True, blank=True)
#     createdAt = models.DateTimeField(auto_now_add=True)
#     _id = models.AutoField(primary_key=True, editable=False)

#     def __str__(self):
#         return str(self.createdAt)

class Book(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE)
    booked_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[(
        'Pending', 'Pending'), ('Confirmed', 'Confirmed')], default='Pending')

    _id = models.AutoField(primary_key=True, editable=False)

    def __str__(self):
        return f"{self.user.username} booking for {self.professional.name}"


class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    # class Meta:
    #     ordering = ['complete']


class Post(models.Model):
    title = models.CharField(max_length=200)
    body = models.TextField(default='yoyo')
    categories = models.ForeignKey(
        Categories, on_delete=models.SET_NULL, null=True, default=1)

    locations = models.CharField(max_length=200, default='Unknown')
    start_time = models.DateTimeField(max_length=20, null=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField(
        auto_now_add=True, null=True)
    modified_date = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return self.title
