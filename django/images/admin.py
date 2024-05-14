from django.contrib import admin

# Register your models here.
from .models import Image, ImageTag

admin.site.register(Image)

admin.site.register(ImageTag)