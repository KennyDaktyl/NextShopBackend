from django.urls import path

from .views import ArticlesDetailsView, ArticlesListView

urlpatterns = [
    path("", ArticlesListView.as_view(), name="articles-list"),
    path(
        "<slug:slug>/", ArticlesDetailsView.as_view(), name="articles-details"
    ),
]
