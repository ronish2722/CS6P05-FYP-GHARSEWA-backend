# Generated by Django 4.1.6 on 2023-03-30 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_professional_rating'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='professional',
            name='numReviews',
        ),
        migrations.RemoveField(
            model_name='professional',
            name='rating',
        ),
    ]
