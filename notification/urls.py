from django.urls import path
from .views import *

urlpatterns = [
    path("", GetNotifications.as_view()),
    path("unread", GetUnreadNotificationNumber.as_view())
]