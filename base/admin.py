from django.contrib import admin
from django.contrib import messages

# Register your models here.

# from .models import Task


from .models import *
# admin.site.register(Professional)
admin.site.register(Review)
admin.site.register(Book)
admin.site.register(Task)
admin.site.register(UserProfile)
admin.site.register(Post)
admin.site.register(Categories)


class ProfessionalAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_approved')
    actions = ['approve_selected', 'decline_selected']

    def approve_selected(self, request, queryset):
        updated_count = queryset.update(is_approved=True)
        messages.success(
            request, f'Successfully approved {updated_count} professional registrations.')
    approve_selected.short_description = 'Approve selected professional registrations'

    def decline_selected(self, request, queryset):
        updated_count = queryset.update(is_approved=False)
        messages.success(
            request, f'Successfully declined {updated_count} professional registrations.')
    decline_selected.short_description = 'Decline selected professional registrations'


admin.site.register(Professional, ProfessionalAdmin)
