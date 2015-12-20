from django.db import models
import os
from django.conf import settings


class Movie(models.Model):
    title = models.CharField(max_length=100)
    path = models.CharField(max_length=1024, unique=True)
    date = models.DateField(null=True, blank=True)
    imdbid = models.CharField(max_length=9, null=True, blank=True)
    poster = models.ImageField(upload_to="posters", null=True, blank=True)

    def path_to_static(self):
        return os.path.join(settings.MEDIA_URL, 'films', os.path.basename(self.path))


    class Meta:
        ordering = ['title']
