from django.db import models
from django.utils import timezone
import django_tables2 as tables
from django.contrib.auth.models import User
from dal import autocomplete
# Create your models here.

# TODO: DONE! -- Integrate user model
# TODO: DONE! -- On tagging of Article, record which user has updated
# TODO: On article page, keyboard shortcuts for next, prev
# TODO: On article page, swipe next-prev for mobile
# TODO: Make mobile UI (fix header)
# TODO: Add footer
# TODO: Make statistics page with plot.ly
# TODO: Not logged in user throws an "User matching query does not exist." error now since it requires an user instance
#       at TagRecord. Implement authentication to views and show some you should login error.
# TODO: Refactor Article2 model to Article.
# TODO: DONE! On edit, fix two times clicking error. Also, enable greater control over deletion
#       and modification on TagRecords.
# TODO: double clicking have been cleared out, but a new flow has been selected. TagRecords are shown as badges,
#       with deletion support. But you still have to clean the code like for things like edit button, for it you pass
#       a variable to show_article. Things like this should be cleaned.

class PffReport(models.Model):
    file_url = models.URLField()
    name = models.CharField(max_length=256)
    month = models.IntegerField(blank=True)
    year = models.IntegerField()

    def __str__(self):
        return self.name

class Tag(models.Model):
    english = models.CharField(max_length=256)
    turkish = models.CharField(max_length=256)
    category = models.CharField(max_length=256)
    category_turkish = models.CharField(max_length=256)
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
    edited_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.PROTECT)
    is_processed = models.BooleanField(default=False)
    process_timestamp = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, through='TagRecord', blank=True)
    related_pff_report = models.ForeignKey(PffReport, on_delete=models.PROTECT)
    class Meta:
        ordering = ("pk", )

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('show_article_url', args=[str(self.article_id)])


class TagRecord(models.Model):
    article2_id = models.ForeignKey(Article2, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)
    number_of_occurence = models.IntegerField(default=1)
        # This field is to keep track of how many times this item
        # should be counted. Came as a request of the project team.
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)





class ArticlesTable(tables.Table):
    article_id = tables.Column(linkify=True, verbose_name="ID")
    tags = tables.ManyToManyColumn(linkify_item=True)

    class Meta:
        model = Article2
        template_name = "django_tables2/bootstrap.html"
        exclude = ("created_at", "is_processed", "process_timestamp", )

class TagsTable(tables.Table):
    id = tables.Column(linkify=True)
    count = tables.Column()
    class Meta:
        model = Tag
        template_name = "django_tables2/bootstrap.html"
        exclude = ("english", "category", "slug",)

class ArticleComment(models.Model):
    comment_text = models.TextField()
    related_user = models.ForeignKey(User, on_delete=models.PROTECT)
    related_article = models.ForeignKey(Article2, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now=True)


# DASH APP
