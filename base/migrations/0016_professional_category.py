# Generated by Django 4.1.6 on 2023-03-28 14:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0015_alter_categories_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='professional',
            name='category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.categories'),
        ),
    ]
