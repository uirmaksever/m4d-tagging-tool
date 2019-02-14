# Generated by Django 2.1.5 on 2019-02-10 17:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('newspaper_scraper', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='article2',
            name='tags',
        ),
        migrations.AddField(
            model_name='article2',
            name='tags',
            field=models.ManyToManyField(blank=True, through='newspaper_scraper.TagRecord', to='newspaper_scraper.Tag'),
        ),
        migrations.AddField(
            model_name='tagrecord',
            name='article2_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newspaper_scraper.Article2'),
        ),
        migrations.AddField(
            model_name='tagrecord',
            name='created_by',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='tagrecord',
            name='tag_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='newspaper_scraper.Tag'),
        ),
    ]
