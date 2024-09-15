from django.urls import path

from .views import ArticlesDetailsView, ArticlesListView, ArticlesPathListView

urlpatterns = [
    path("", ArticlesListView.as_view(), name="articles-list"),
    path(
        "articles-path-list/",
        ArticlesPathListView.as_view(),
        name="articles-list-path",
    ),
    path(
        "<slug:slug>/", ArticlesDetailsView.as_view(), name="articles-details"
    ),
]
