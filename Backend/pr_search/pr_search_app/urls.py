from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/versions/", views.get_versions, name="get_versions"),
    path("api/search/", views.search_documents, name="search_documents"),
]
