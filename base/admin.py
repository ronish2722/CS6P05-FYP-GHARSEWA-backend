from django.contrib import admin

# Register your models here.

# from .models import Task
# admin.site.register(Task)


from .models import *
admin.site.register(Professional)
admin.site.register(Review)
admin.site.register(Book)
