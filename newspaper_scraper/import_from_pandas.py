from newspaper_scraper.models import Article2, Tag
import pandas
import datetime
import pytz

articles_pd = pandas.read_excel("D:/Libraries/Google Drive/Media4Democracy/Press for Freedom Raporları/2018/export_2.xlsx", )
tags_pd = pandas.read_excel("D:/Libraries/Google Drive/Media4Democracy/Press for Freedom Raporları/2018/tags.xlsx")

def import_articles_to_db(pd):
    articles_to_import = []
    for article in pd.index:
        article_id = pd["article_id"][article]
        category = pd["category"][article]
        event_date = pd["date_corrected"][article]
        print(type(event_date))
        event_date = datetime.datetime.date(event_date)
        text = pd["text_without_ref"][article]
        single_article = Article2(
            article_id=article_id,
            category=category,
            event_date=event_date,
            text=text)
        articles_to_import.append(single_article)

    Article2.objects.bulk_create(articles_to_import)

def import_tags_to_db(pd):
    tags_to_import = []
    for tag in pd.index:
        category = pd["category"][tag]
        slug = pd["slug"][tag]
        turkish = pd["turkish"][tag]
        english = pd["english"][tag]
        single_tag = Tag(
            category=category,
            slug=slug,
            turkish=turkish,
            english=english
        )
        tags_to_import.append(single_tag)
    Tag.objects.bulk_create(tags_to_import)

