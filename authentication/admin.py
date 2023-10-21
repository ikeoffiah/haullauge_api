from django.contrib import admin
from .models import User, Agents, Drivers

admin.site.register(User)
admin.site.register(Agents)
admin.site.register(Drivers)

