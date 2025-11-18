from django.contrib import admin
from .models import UserProfile

# Register your models here.

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'username','role','email')
    list_filter = ('role',)
    search_fields = ['first_name', 'last_name','last_name']
    empty_value_display = '-empty-'

admin.site.register(UserProfile,UserProfileAdmin)