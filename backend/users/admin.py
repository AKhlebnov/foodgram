from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ('avatar_display',)

    def avatar_display(self, obj):
        if obj.avatar:
            return (
                format_html(
                    '<img src="{}" width="50" height="50" />', obj.avatar.url
                )
            )
        else:
            return '(No image)'

    avatar_display.allow_tags = True
    avatar_display.short_description = 'Avatar'


CustomUserAdmin.fieldsets += (
    ('Extra Fields', {'fields': ('avatar', )}),
)

admin.site.register(User, CustomUserAdmin)
