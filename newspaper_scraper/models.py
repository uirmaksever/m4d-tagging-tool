from django.db import models
from django.utils import timezone
import django_tables2 as tables
from dal import autocomplete
# Create your models here.

# TODO: Integrate user model
# TODO: On tagging of Article, record which user has updated
# TODO: On article page, keyboard shortcuts for next, prev
# TODO: On article page, swipe next-prev for mobile
# TODO: Make mobile UI (fix header)
# TODO: Add footer
# TODO: Make statistics page with plot.ly


class Tag(models.Model):
    english = models.CharField(max_length=256)
    turkish = models.CharField(max_length=256)
    category = models.CharField(max_length=256)
    slug = models.CharField(max_length=256)

    def __str__(self):
        return self.turkish

    def get_absolute_url(self):
        return "/tags/%i" % self.id


class Article2(models.Model):
    article_id = models.IntegerField(primary_key=True)
    category = models.TextField()
    event_date = models.DateField(default=timezone.now)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    process_timestamp = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ("pk", )

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('show_article_url', args=[str(self.article_id)])


class ArticlesTable(tables.Table):
    article_id = tables.Column(linkify=True, verbose_name="ID")
    tags = tables.ManyToManyColumn(linkify_item=True)

    class Meta:
        model = Article2
        template_name = "django_tables2/bootstrap.html"


class TagsTable(tables.Table):
    id = tables.Column(linkify=True)
    count = tables.Column()
    class Meta:
        model = Tag
        template_name = "django_tables2/bootstrap.html"
