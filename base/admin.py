from django.contrib import admin

# Register your models here.

# from .models import Task


from .models import *
admin.site.register(Professional)
admin.site.register(Review)
admin.site.register(Book)
admin.site.register(Task)
admin.site.register(UserProfile)
admin.site.register(Post)
