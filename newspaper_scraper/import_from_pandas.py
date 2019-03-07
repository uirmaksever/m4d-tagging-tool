# Please don't let remain any executable code in this file. It is for some handy shortcut functions you want
# to run from time to time.

from newspaper_scraper.models import Article2, Tag, TagRecord
import pandas
import datetime
import pytz
from django.utils import timezone
from django.db import connection


def import_articles_to_db(pd):
    articles_pd = pandas.read_excel("D:/Libraries/Google Drive/Media4Democracy/Press for Freedom Raporları/2018/export_2.xlsx", )
    tags_pd = pandas.read_excel("D:/Libraries/Google Drive/Media4Democracy/Press for Freedom Raporları/2018/tags.xlsx")
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

credential_json = {
  "type": "service_account",
  "project_id": "project-id-6243632242343096428",
  "private_key_id": "b57241534428f9289ab5bc7af314d3118f1b77de",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDI7twpVbf9mdrg\nguDRA+F/mep9A7QQQ1+QbmbpGFs9y+rAtEoZDHvYtR7xEXJeLiAqD93BOzLACQeu\n2wz39ddfsj09xK2saCtgvp/Rxd0u3rDTrN8ZGmH8t10SGxiqZyfH4UJa5n+CsJgY\nUADUI/s89vVtW3uZGJrytREzTMQaRsuaelzPXMPNTssSm7RzsLl/Od3Yq59sBG3Q\nJFzhLU78TWyrSx95AWxcY+AsDtKbOf1v2Z4elOqJnn3Na/Sp9+FkTaEHFLxzfI9g\npGc9N1Le9T72dWJs0qwc29tamSJOj9YiK40r5vpFcgGxytg7GKYBwED5z7PKbCQU\n/vsgml8PAgMBAAECggEAFrtAXflsE2fHUBSOXCcNE5NKk10KubedhT3wLNj2uDLX\nD85K/wgfWgCs4PHWgfAZmcM/akpeWe+g67etVmn8tRSkLVY68vZlSJBtjTJOF6zV\neAT7x5++oR6aDAp+YQdtg9p92Bcb1Xb7+0LQbS+AOevoZQ2Z7ykjnRHolxNNW3lz\n3IdeGsoc94WlOeFqoL++OOhXpBKXYwQIiyWIKKjX5svUttC6mmjSyhCMUeSbxYx3\nUxuzUsQ8IPgyfDbm/smHuBWqO9Z8JGpI9dA6Es1oaJw10aBMsfnoZkN378eADhI4\ncy/8w0ZWJIDQrXG6Fv7WdavWn+dhQ7igJo5OyJ6Y6QKBgQDqIPvjwGCJojAf2kM5\n+dC1h56KvQJ79OSPt4hbOmwAW+d9h5D9ye+T05imz4wTYAQaayVpXKewHJCzxuQ7\na52TfdLZ06idFn8zM1yOl8dg219+jf1KiBiU2FaR62KOGuw1DjaXt21gc23cUNZh\n+uCjnxiOrUUxIHbqhb8MNQoKVwKBgQDbtAX/lPW1sfkDP+WMz4zq/IThI2AkFUj1\nziPtx4XHJLh5YX6ouFNtBDi3yKIoD2QxoaWFt2qfP3WQ7Jd2G52/7rUHOOwOmOwS\nQ+bgfSwFQdvXVEKWCh+b5DU+Llv/CrsM4Qv5SMsEIiWTKiTtX0qKiWLACHBvgjO/\ntT/xz8LOCQKBgD98gDEq2kKX+yq3+aC/7+s5gjEmvYS1TED4SH5MYjrasPPmDdfz\nqQZRy0P4ZYhfcd1kDnn6iPIFXOuS1BKUxN7YsJMmhMNL9WQB2mhEGelWsxdTE0rh\niqDZ5Oeeh1P3UvO0DfOn5n3P7wtd1DQvXjigDH2r2GZQ4k4HxF1gCH/zAoGAJVhg\nfKVRbuUlssu1tU3CYl8yJyLgQMHtePrlWJHFx6gSQ2+zG/LZG3rQOU09YxnaqiUU\nAbq/wPoEffH5fPYMxodI9kVSuth7qE8qe5ZLWUlsmRmVh/OIk/MiqcMvmBa23OWU\nJ3ecKsOzJ2TOihrcjNf1lTbaBdpX+YpRqETslCECgYEArmw0saxVnWrXI5AGCOxZ\nnasmEaYZcIfc90m85RQqAw8I//WyG9sdPZ4wlt1PQYhohHKS6yFZkAhHEhlb0PAo\nGIQeQrGWfT2XSCIJAnMmOtHNiV/d9yaQwgBlReKlZC078EJTryN1lSbzAToRxXkN\nvUdSoglzQr7P8JDtwG+tT0A=\n-----END PRIVATE KEY-----\n",
  "client_email": "wordpress@project-id-6243632242343096428.iam.gserviceaccount.com",
  "client_id": "103382788330341818619",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/wordpress%40project-id-6243632242343096428.iam.gserviceaccount.com"
}

def push_to_sheets(query):
    import gspread
    from gspread_dataframe import set_with_dataframe
    from oauth2client.service_account import ServiceAccountCredentials

    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_name(credential_json, scope)
    gs = gspread.authorize(credentials)
    worksheet = gs.open_by_key('1ZULxpH-U3JPkC7q7l1xeFX7Aw95l6kEnlveePAqmvh8').sheet1
    worksheet.clear()
    query_pd = pandas.read_sql(query, connection)
    set_with_dataframe(worksheet=worksheet, dataframe=query_pd)
    print("Done and done")
    connection.close()


# from django.db.models import Count, Min
# all = TagRecord.objects.order_by('article2_id').values('article2_id', 'tag_id', 'id')
# for article in Article2.objects.all():
#     article_id = article.article_id
#     bound_tags = TagRecord.objects\
#         .filter(article2_id=article_id)\
#         .values('article2_id', 'tag_id',).annotate(Count('article2_id')).filter(article2_id__count__gt=1)
#     bound_tags = list(bound_tags)
#     # if len(bound_tags) > 1:
#     print(article_id, bound_tags, len(bound_tags))
#     #else:
#         # print('just one')
