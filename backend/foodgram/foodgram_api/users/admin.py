from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'password')
    search_fields = ('username', 'email')
    list_filter = ('username', 'email')


admin.site.register(User, UserAdmin)
