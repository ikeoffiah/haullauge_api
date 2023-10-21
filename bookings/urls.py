from django.urls import path
from .views import *

urlpatterns = [
    path('', BookingView.as_view()),
    path('hauls', HaulsView.as_view()),
    path('hauls/', GetHaulByStatus.as_view()),
    path('hauls/<uuid:pk>', HaulUpdateView.as_view()),
    path('file-upload', UploadImageFile.as_view()),
    path('hauls/driver', GetAllHaulsView.as_view()),
    path('hauls/driver/', FilterHaul.as_view()),
    path('hauls/driver/user/', GetDriverHauls.as_view()),
    path('hauls/driver/<uuid:pk>', AcceptHaulView.as_view())
]