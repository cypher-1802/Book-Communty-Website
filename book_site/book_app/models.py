from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class User(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    email = models.EmailField()
    password = models.CharField(null = True, max_length = 20)
    to_read_list = models.TextField(null = True)
    library = models.TextField(null = True)

    def __str__(self):
        return str(self.user.username)

class Discussion(models.Model):
    username = models.ForeignKey(User, null = True, on_delete = models.CASCADE)
    book_id = models.CharField(null = True, max_length = 20)
    #created_on = models.
    message = models.TextField(null = True)

    def __str__(self):
        return str(self.book_id)

class Read(models.Model):
    username = models.ForeignKey(User, null = True, on_delete = models.CASCADE)
    book_id = models.CharField(null = True, max_length = 20)
    to_read = models.BooleanField(null = True)
    finished = models.BooleanField(null = True)

    def __str__(self):
        return str(self.book_id)

class Add_Books(models.Model):
    username = models.ForeignKey(User, null = True, on_delete = models.CASCADE)
    book_id = models.CharField(null = True, max_length = 20)
    format = models.CharField(null = True, max_length = 20)      #softcopy or hardcopy
    contact = models.CharField(null = True, max_length = 20)     #contact method to be decided
    message = models.TextField(null = True)     #if any

    def __str__(self):
        return str(self.book_id)
 
class Books(models.Model):
    ISBN = models.CharField(null = True, max_length = 20)
    name = models.CharField(null = True, max_length = 40)
    cover = models.ImageField(upload_to = None)
    author = models.CharField(null = True, max_length = 20)
    genre = models.CharField(null = True, max_length = 20)
    summary = models.TextField(null = True)
    #rating = models.
    discussion = models.ForeignKey(Discussion, null = True, on_delete = models.CASCADE)
    read = models.ForeignKey(Read, null = True, on_delete = models.CASCADE)
    trade = models.ForeignKey(Add_Books, null = True, on_delete = models.CASCADE)

    def __str__(self):
        return str(self.ISBN)
