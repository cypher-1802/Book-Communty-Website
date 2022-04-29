from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login', views.user_login, name = 'login'),
    path('logout', views.user_logout, name = 'logout'),
    path('signup', views.user_signup, name = 'signup'),
    path('Main', views.main, name = 'main'),# make a view function for main
    path('search/<str:name>', views.search, name = 'search'),
    path('book_preview/<str:id>', views.book_preview, name = 'book_preview'),
    path('trd', views.trd, name = 'trd'),
    path('trade/<str:id>', views.trade, name = 'trade'),
    path('add/<str:id>', views.add_books, name = 'add'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)