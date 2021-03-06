from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponse
from . import forms
from django.utils import timezone
from .models import Article2, ArticlesTable, Tag, TagsTable, TagRecord, PffReport, ArticleComment
from django.views.generic.edit import DeleteView
from next_prev import next_or_prev_in_order
from django.contrib import messages
from dal import autocomplete
from django.contrib.auth.models import User
from django.urls import reverse
import logging
from . import tasks
from .import_from_pandas import push_to_sheets, query
import pandas
import datetime

logger = logging.getLogger('scraper_logger')
# Create your views here.


# def process(url):
#     downloaded_article = newspaper.Article(url)
#     downloaded_article.download()
#
#     created_article = models.Article.objects.create(
#         title = downloaded_article.title,
#         body = downloaded_article.text,
#         timestamp = datetime.datetime.now().timestamp(),
#         # publish_date = downloaded_article.publish_date,
#         source_url = forms.UrltoFetch.objects.get(url=url)
#         # source_newspaper =
#     )
#     # created_article = models.Article()
#     # created_article.title = downloaded_article.title
#     # created_article.body = downloaded_article.text
#     # created_article.publish_date = downloaded_article.publish_date
#     # # created_article.source_url = url
#     # # created_article.source_newspaper = downloaded_article.meta_site_name
#
#     return created_article


def index_page(request):
    return render(request, "index.html")


def show_article(request, article_id, edit=False):
    returned_article = Article2.objects.get(article_id=article_id)
    category_field = getattr(returned_article, "category")
    eventdate_field = getattr(returned_article, "event_date")
    text_field = getattr(returned_article, "text")
    related_pff_report = returned_article.related_pff_report
    # is_processed_field = getattr(returned_article, "is_processed")
    tagrecords_field = TagRecord.objects.filter(article2_id=article_id)  # getattr(returned_article, "tags")
    # Next-prev
    qs_filtered = Article2.objects.filter(tags__isnull=True)
    next_article = next_or_prev_in_order(returned_article, qs=qs_filtered, loop=True)
    prev_article = next_or_prev_in_order(returned_article, qs=qs_filtered, prev=True, loop=True)
    if next_article is not None:
        next_article_url = request.build_absolute_uri(next_article.get_absolute_url())
    else:
        next_article_url = "#"
    if prev_article is not None:
        prev_article_url = request.build_absolute_uri(prev_article.get_absolute_url())
    else:
        prev_article_url = "#"
    article_dictionary = {
        "article_id": article_id,
        "category": category_field,
        "event_date": eventdate_field,
        "text": text_field,
        # "is_processed": is_processed_field,
        "tagrecords": tagrecords_field,
        "next": next_article_url,
        "prev": prev_article_url,
        "edit_form_link": returned_article.get_absolute_url() + "edit",
        "related_pff_report": related_pff_report
    }

    # if edit is True:
    #     returned_article.is_processed = False
    #     returned_article.save()

    # if returned_article.is_processed is False:
    form = forms.TaggingForm
    article_dictionary["tagging_form"] = form
    comment_form = forms.ArticleCommentForm
    article_dictionary["comment_form"] = comment_form
    related_comments = ArticleComment.objects.filter(related_article=returned_article)
    article_dictionary["related_comments"] = related_comments
    print(related_comments)
    # else:
    #   pass
    print(returned_article)
    if request.method == "POST":
        tag_form = forms.TaggingForm(request.POST)
        comment_form = forms.ArticleCommentForm(request.POST)
        if "submit_tag_button" in request.POST and tag_form.is_valid():
            print(tag_form.cleaned_data["tags"])
            if not tag_form.cleaned_data["tags"]:
                # To prevent empty form submission
                messages.warning(request, "You have not selected any tag for this article")
            else:
                # returned_article.is_processed = True
                print(tag_form.cleaned_data["tags"])

                for tag_selection in tag_form.cleaned_data["tags"].iterator():
                    TagRecord.objects.create(
                        article2_id=returned_article,
                        tag_id=tag_selection,
                        number_of_occurence=tag_form.cleaned_data["number_of_occurence"],
                        created_by=User.objects.get(username=request.user)
                    )
                    tasks.task_push_to_sheets.delay()
                logger.info("[{}] New TagRecord entry on Article {}, by {}".format(
                    timezone.now(),
                    returned_article.article_id,
                    request.user))
                # form.save_m2m()
                returned_article.process_timestamp = timezone.now()
                returned_article.save()
        if "comment_button" in request.POST and comment_form.is_valid():
            comment = ArticleComment.objects.create(
                related_article=returned_article,
                related_user=request.user,
                comment_text=comment_form.cleaned_data["comment_text"]
            )
            comment.save()
            messages.success(request, "Comment saved successfully")
            print("Comment saved.")
        else:
            messages.warning(request, "There have been an error while submitting the record.")
    return render(request, "single_article.html", article_dictionary)


def show_all_articles(request):
    all_articles = Article2.objects.all().order_by('-article_id')
    table = ArticlesTable(all_articles)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    return render(request, "all_articles.html", {"articles_table": table})

# def create_comment(request, article_id):
#     related_article = Article2.objects.get(pk=article_id)
#
#     if request.method == "POST":
#         pass
#     return HttpResponse("Commenting on: {}, {}".format(article_id, related_article.text))

def show_tag(request, id):
    returned_tag = Tag.objects.get(id=id)
    returned_articles_based_on_tag = Article2.objects.filter(tags__in=[returned_tag.id])
    table = ArticlesTable(returned_articles_based_on_tag)
    print(returned_articles_based_on_tag)
    turkish_name = returned_tag.turkish
    return render(request, "all_articles.html", {"articles_table": table})


def show_all_tags(request):
    all_tags = Tag.objects.all()
    table = TagsTable(all_tags)
    return render(request, "all_tags.html", {"tags_table": table})


def start_tagging(request):
    import random
    not_processed_articles = Article2.objects.filter(tags__isnull=True).order_by("article_id")
    first_not_processed_article_id = not_processed_articles.first().article_id
    # ids_list = []
    # for article in empty_articles:
    #     article_id = article.article_id
    #     ids_list.append(article_id)
    # print(ids_list)
    # random.choice(ids_list)
    # random_not_processed = random.choice(ids_list)
    logger.info("[{}] User: {} entered into start_tagging on Article {}",format(
        timezone.now(), request.user, first_not_processed_article_id
    ))
    return show_article(request, first_not_processed_article_id)


class TagAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = Tag.objects.all()

        # receives selected categories from form object
        categories = self.forwarded.get("categories", None)

        # filters categories here
        if categories:
            qs = qs.filter(category_turkish=categories)
        if self.q:
            print(self.q)
            qs = qs.filter(category_turkish=self.q)
            print(qs)

        return qs


def get_user_profile(request, username):
    user = User.objects.get(username=username)
    tags_count_per_user = TagRecord.objects.filter(created_by=user).count()
    print(tags_count_per_user)
    return render(request, 'registration/user.html', {"user": user, "tags_count_per_user": tags_count_per_user})


class TagRecordDelete(DeleteView):
    model = TagRecord
    pk_field = TagRecord._get_pk_val


    # This function overrides default confirmation process of DeleteView, you should not go over confirmation template.
    def get_success_url(self):
        tag_record_id = self.kwargs["pk"]
        deleted_tagrecord = TagRecord.objects.get(pk=tag_record_id)
        article_id = deleted_tagrecord.article2_id_id
        print(article_id)
        logger.info("[{}] TagRecord {} has been deleted on Article {} by User {}".format(
            timezone.now(), deleted_tagrecord.id, article_id, self.request.user
        ))
        return reverse("show_article_url", kwargs={"article_id": article_id})

def statistics(request):
    number_of_processed_articles = Article2.objects.exclude(tagrecord__isnull=False).count()
    number_of_not_processed_articles = Article2.objects.exclude(tagrecord__isnull=True).count()
    number_of_articles = Article2.objects.all().count()
    context = {
        'number_of_processed_articles': number_of_processed_articles,
        'number_of_not_processed_articles': number_of_not_processed_articles,
        'number_of_articles': number_of_articles
    }
    from django.db.models import Count, Sum
    import json
    count_dict = {}

    for category in Tag.objects.values_list("category_turkish").distinct():
        articles_per_tag = Tag.objects\
            .filter(category_turkish=category[0])\
            .annotate(count=Count('tagrecord'))\
            .values("turkish", "count")
        count_dict[category] = articles_per_tag
        print(category[0])
    print(count_dict)
    push_to_sheets(query)
    return render(request, "statistics.html", context)


def import_articles_to_db(request):
    articles_pd = pandas.read_excel("/Users/umutirmaksever/Downloads/export_edited.xlsx", )
    # tags_pd = pandas.read_excel("D:/Libraries/Google Drive/Media4Democracy/Press for Freedom Raporları/2018/tags.xlsx")
    articles_to_import = []
    for article in articles_pd.index:
        article_id = articles_pd["import_id"][article] # You added id field manually into excel file
        category = articles_pd["category"][article]
        event_date = articles_pd["date_corrected"][article]
        print("Adding {}".format(article_id))
        event_date = datetime.datetime.date(event_date)
        text = articles_pd["text_without_ref"][article]
        single_article = Article2(
            article_id=article_id,
            category=category,
            event_date=event_date,
            text=text,
            related_pff_report= PffReport.objects.get(pk=3))
        articles_to_import.append(single_article)
    print("Started bulk import.")
    Article2.objects.bulk_create(articles_to_import)
    return render(request, "upload_articles_success.html")
