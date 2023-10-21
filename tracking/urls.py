from .views import *
from django.urls import path

urlpatterns = [
    path('track/<uuid:pk>', UpdateTrackingView.as_view())
]