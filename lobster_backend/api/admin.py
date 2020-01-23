from django.contrib import admin
from .models import User, UserRelations, Post, Photo

admin.site.register(User)
admin.site.register(UserRelations)
admin.site.register(Post)
admin.site.register(Photo)
