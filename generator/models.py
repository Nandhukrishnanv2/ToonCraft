from django.db import models

# Create your models here.
# generator/models.py
from django.contrib.auth.models import User

class Image(models.Model):
    name = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    tag = models.CharField(max_length=100, blank=True, null=True)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class images(models.Model):
    user=models.ForeignKey(User,related_name='user_profile',on_delete=models.CASCADE)
    image=models.ImageField(upload_to='media/')


