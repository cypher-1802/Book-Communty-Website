from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Discussion)
admin.site.register(Books)
admin.site.register(Add_Books)
admin.site.register(Read)
