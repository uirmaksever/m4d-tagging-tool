from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.http import HttpResponse
from . import forms
from django.utils import timezone
from .models import Article2, ArticlesTable, Tag, TagsTable, TagRecord
from django.views.generic.edit import DeleteView
from next_prev import next_or_prev_in_order
from django.contrib import messages
from dal import autocomplete
from django.contrib.auth.models import User
from django.urls import reverse
import logging

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
        "edit_form_link": returned_article.get_absolute_url() + "edit"
    }

    # if edit is True:
    #     returned_article.is_processed = False
    #     returned_article.save()

    # if returned_article.is_processed is False:
    form = forms.TaggingForm
    article_dictionary["tagging_form"] = form
    # else:
    #   pass
    print(returned_article)
    if request.method == "POST":
        form = forms.TaggingForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data["tags"])
            if not form.cleaned_data["tags"]:
                # To prevent empty form submission
                messages.warning(request, "You have not selected any tag for this article")
            else:
                # returned_article.is_processed = True
                print(form.cleaned_data["tags"])

                for tag_selection in form.cleaned_data["tags"].iterator():
                    TagRecord.objects.create(
                        article2_id=returned_article,
                        tag_id=tag_selection,
                        number_of_occurence=form.cleaned_data["number_of_occurence"],
                        created_by=User.objects.get(username=request.user)
                    )
                logger.info("[{}] New TagRecord entry on Article {}, by {}".format(
                    timezone.now(),
                    returned_article.article_id,
                    request.user))
                # form.save_m2m()
                returned_article.process_timestamp = timezone.now()
                returned_article.save()
        else:
            messages.warning(request, "There have been an error while submitting the record.")
    return render(request, "single_article.html", article_dictionary)


def show_all_articles(request):
    all_articles = Article2.objects.all().order_by('-article_id')
    table = ArticlesTable(all_articles)
    table.paginate(page=request.GET.get("page", 1), per_page=10)
    return render(request, "all_articles.html", {"articles_table": table})


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
    return render(request, "statistics.html", context)