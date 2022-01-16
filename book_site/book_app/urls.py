from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name = 'home'),
    path('login', views.login, name = 'login'),
    path('logout', views.logout, name = 'logout'),
    path('search', views.search, name = 'search'),
    path('book_preview/<str:id>', views.book_preview, name = 'book_preview'),
]