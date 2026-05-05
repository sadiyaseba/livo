from django.contrib import admin
from posts.models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'user', 'availability', 'created_at')
    list_filter = ('type', 'availability')
    search_fields = ('title', 'description', 'user__username')
