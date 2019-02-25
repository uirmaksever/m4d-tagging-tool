# Please don't let remain any executable code in this file. It is for some handy shortcut functions you want
# to run from time to time.

from newspaper_scraper.models import Article2, Tag
import pandas
import datetime
import pytz
from django.utils import timezone
from django.db import connection

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


def delete_records_of_category(category_name):
    articles = Article2.objects.filter(category=category_name)
    deleted_articles_file = open("backups/deleted_articles {}.txt".format(category_name), "a+", encoding="utf-8")
    print(articles)
    number_of_deleted_articles = len(articles)
    deleted_articles_file.write("Number of deleted articles: " + str(number_of_deleted_articles) + "\n")
    deleted_articles_file.write("Deleted at: " + str(timezone.now()) + "\n")
    for article in articles:
        deleted_article_string = str(article.article_id) + \
                                 " - " + str(article.category) + \
                                 " - " + str(article.text) + \
                                 " - " + str(article.event_date) + \
                                 "\n"
        deleted_articles_file.write(deleted_article_string)
        print("Deleting: {}".format(article.article_id))
        article.delete()
    deleted_articles_file.close()


# PUSH TO GOOGLE SHEETS CUSTOM QUERY

query = """
    SELECT newspaper_scraper_tagrecord.id as record_id,
           newspaper_scraper_tagrecord.number_of_occurence as record_number_of_occurence,
           newspaper_scraper_tagrecord.tag_id_id as record_tag_id,
           newspaper_scraper_tagrecord.article2_id_id as record_article_id,
           newspaper_scraper_tag.id as tag_id,
           newspaper_scraper_tag.category as tag_levelone,
           newspaper_scraper_tag.english as tag_level2,
           n.article_id as article_id,
           n.category as article_category,
           n.event_date as article_event_date,
           n.text as article_text
    FROM newspaper_scraper_tagrecord
    JOIN newspaper_scraper_tag on newspaper_scraper_tagrecord.tag_id_id = newspaper_scraper_tag.id
    JOIN newspaper_scraper_article2 n on newspaper_scraper_tagrecord.article2_id_id = n.article_id
"""

def get_credentials(query_file_name):
    from oauth2client.client import OAuth2Credentials, GoogleCredentials
    credential_file = open(query_file_name).read()
    print(credential_file)
    auth_client = GoogleCredentials.from_json(credential_file)
    auth_client.get_access_token()

    return auth_client

def push_to_sheets(query):
    from df2gspread import df2gspread as d2g

    query_pd = pandas.read_sql(query, connection)
    print(query_pd)
    credential_filename = '.gdrive_private.json'
    spreadsheet = ('1ECpOJ1QuFGbFdszlN-W-3a1C95zD1sKtpBEJcZsXUmI')
    sheet_name = "Automatic Push to Sheets"

    credentials = get_credentials(credential_filename)
    d2g.upload(query_pd, spreadsheet, wks_name=sheet_name)
    return query_pd

push_to_sheets(query)