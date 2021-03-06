# Generated by Django 2.1.5 on 2019-02-08 00:24

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Article2',
            fields=[
                ('article_id', models.IntegerField(primary_key=True, serialize=False)),
                ('category', models.TextField()),
                ('event_date', models.DateField(default=django.utils.timezone.now)),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_processed', models.BooleanField(default=False)),
                ('process_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ('pk',),
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('english', models.CharField(max_length=256)),
                ('turkish', models.CharField(max_length=256)),
                ('category', models.CharField(max_length=256)),
                ('slug', models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name='article2',
            name='tags',
            field=models.ManyToManyField(blank=True, to='newspaper_scraper.Tag'),
        ),
    ]
