from celery import shared_task

from datetime import datetime

from media.models import Post


@shared_task
def publishing_post() -> None:
    current_time = datetime.now()
    queryset = Post.objects.filter(published_date__lte=current_time)
    for post in queryset:
        post.is_published = True
        post.save()
