from django.db import models
from django.contrib.auth.models import User
import os, random

# Create your models here.
class Book_User(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    image = models.ImageField(upload_to = 'images/users', default = 'images/default/' + random.choice(os.listdir(path = 'media/images/default')))
    bio = models.CharField(null = True, blank = True, max_length = 100)
    following = models.TextField(null = True, blank = True)
    followers = models.TextField(null = True, blank = True)
    to_read_list = models.TextField(null = True, blank = True)
    library = models.TextField(null = True, blank = True)

    def __str__(self):
        return str(self.user.username)

class Discussion(models.Model):
    username = models.ForeignKey(Book_User, null = True, on_delete = models.CASCADE)
    book_id = models.CharField(null = True, max_length = 20)
    created_on = models.DateTimeField(auto_now_add = True)
    message = models.TextField(null = True)

    def __str__(self):
        return str(self.created_on)

class Read(models.Model):
    username = models.ForeignKey(Book_User, null = True, on_delete = models.CASCADE)
    book_id = models.CharField(null = True, max_length = 20)
    to_read = models.BooleanField(null = True, default = False)
    finished = models.BooleanField(null = True, default = False)

    def __str__(self):
        return str(self.book_id)

class Add_Books(models.Model):
    username = models.ForeignKey(Book_User, null = True, on_delete = models.CASCADE)
    book_id = models.CharField(null = True, max_length = 20)
    format = models.CharField(null = True, max_length = 20)      #softcopy or hardcopy
    contact = models.CharField(null = True, max_length = 20)     #contact method to be decided
    message = models.TextField(null = True)     #if any

    def __str__(self):
        return str(self.book_id)
