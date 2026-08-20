from django.contrib import admin

from .models import Todo

# Register your models here.
"""
class TodoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "body",
    )


"""


class TodoAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "user",
        "completed",
    )

    list_filter = ("completed",)

    search_fields = (
        "title",
        "body",
        "user__username",
    )


admin.site.register(Todo, TodoAdmin)
