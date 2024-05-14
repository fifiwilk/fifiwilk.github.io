from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class ImageTag(models.Model):
    tag = models.CharField(max_length=100)

    def __str__(self):
        return self.tag

class Image(models.Model):
    image_title = models.CharField(max_length=100)
    pub_date = models.DateTimeField('date published')
    width = models.IntegerField(default=100)
    height = models.IntegerField(default=100)
    editors = models.ManyToManyField(User, blank=True)
    tags = models.ManyToManyField(ImageTag, blank=True)
    description = models.CharField(max_length=2000, default='', blank=True)
    
    def __str__(self):
        return self.image_title


class Rectangle(models.Model):
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    x_pos = models.IntegerField()
    y_pos = models.IntegerField()
    width = models.IntegerField()
    height = models.IntegerField()
    fill_color = models.CharField(max_length=20)
    time_added = models.DateTimeField('time added')

