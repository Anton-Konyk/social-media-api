from celery import shared_task

from django.utils import timezone

from media.models import Post


@shared_task
def publishing_post() -> None:
    current_time = timezone.now()
    queryset = Post.objects.filter(scheduled_publish_time__lte=current_time)
    for post in queryset:
        post.is_published = True
        post.save()
