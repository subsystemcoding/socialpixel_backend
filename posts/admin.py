from django.contrib import admin
from .models import Post, Comment
class PostAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ["image"]
        else:
            return []

admin.site.register(Post, PostAdmin)
admin.site.register(Comment)