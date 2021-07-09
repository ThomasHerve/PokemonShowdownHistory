from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import *

admin.site.register(Month)
admin.site.register(Tier)
admin.site.register(Pokemon)

