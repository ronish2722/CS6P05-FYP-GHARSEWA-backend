from django.contrib import admin

# Register your models here.

from .models import Task, Professional
admin.site.register(Task, Professional)
