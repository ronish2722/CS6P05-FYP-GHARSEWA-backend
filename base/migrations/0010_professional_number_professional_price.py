# Generated by Django 4.1.6 on 2023-05-30 04:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0009_alter_book_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='number',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='professional',
            name='price',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]