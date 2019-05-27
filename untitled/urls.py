"""untitled URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from newspaper_scraper import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path("articles/<int:article_id>/", views.show_article, name="show_article_url"),
    # path("articles/<int:article_id>/edit", views.show_article, {"edit": True}, name="edit_article_tags"),
    path("delete/<int:pk>", views.TagRecordDelete.as_view(), name="delete_TagRecord"),
    # TODO: /edit happens on two clicks
    path("articles/", views.show_all_articles),
    path("", views.show_all_articles, name="base_url"),
    path('tag-autocomplete/', views.TagAutocomplete.as_view(), name="tag-autocomplete"),
    path("tags/<int:id>", views.show_tag),
    path("tags/", views.show_all_tags),
    path("start-tagging", views.start_tagging, name="start_tagging"),
    path("users/", include('django.contrib.auth.urls'), name="users"),
    path("users/<str:username>", views.get_user_profile),
    path("statistics/", views.statistics, name= "statistics"),
    path("enter_articles_bulk", views.import_articles_to_db),
    path("articles/<int:article_id>/create_comment", views.show_article, name="create_comment_on_article")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
