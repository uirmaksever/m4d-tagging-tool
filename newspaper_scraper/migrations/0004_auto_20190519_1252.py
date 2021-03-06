# Generated by Django 2.2.1 on 2019-05-19 12:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('newspaper_scraper', '0003_tag_category_turkish'),
    ]

    operations = [
        migrations.AddField(
            model_name='article2',
            name='edited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tagrecord',
            name='number_of_occurence',
            field=models.IntegerField(default=1),
        ),
    ]
