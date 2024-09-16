from django.contrib import admin

from media.models import (
    Profile,
    Post,
    Comment,
    UserReaction,
)


admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(UserReaction)
