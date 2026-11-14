from django.urls import path

from .api import chat


app_name = "chat"

urlpatterns = [
    path("", chat, name="message"),
]
