from django.contrib import admin
from .models import Profile, Post, Comment, Tag
# from .models import Notification

# @admin.register(Notification)
# class NotificationAdmin(admin.ModelAdmin):
#     list_display = ('user', 'message', 'read', 'created_at')
#     list_filter = ('read', 'created_at')
#     search_fields = ('user__username', 'message')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')

class PostAdmin(admin.ModelAdmin):
    list_display = ('author', 'caption', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('caption', 'author__username')

class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'text', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('text', 'author__username')

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Tag)