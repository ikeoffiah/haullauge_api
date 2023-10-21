from django.contrib import admin
from .models import Locations, Bookings, Hauls

admin.site.register(Locations)
admin.site.register(Bookings)
admin.site.register(Hauls)

