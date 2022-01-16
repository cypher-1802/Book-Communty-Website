from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
import requests, json

# Create your views here.
def login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
        return render(request, 'login.html', {'error ' : 'Invalid username or password'})
    return render(request, 'login.html')

def signup(request):
    pass

def logout(request):
    logout(request)

def home(request):
    return render(request, 'home.html')

def search(request, name='boy+in+strpped+pyjama'):
    L = []
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q=intitle:'+name+'&key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['items']
    
    for data in response:
        D = {}
        data_new = data['volumeInfo']
        D['id'] = data['id']
        D['title'] = data_new['title']

        try:
            D['author'] = data_new['authors'] 
        except:
            D['author'] = "NA"

        try:
            D['rating'] = data_new['averageRating']
        except:
            D['rating'] = 'NA'

        try:
            D['cover'] = data_new['imageLinks']['thumbnail']
        except:
            D['cover'] = 'https://image.shutterstock.com/image-vector/no-image-available-icon-fow-260nw-1690416772.jpg'

        L.append(D)

    return render(request, 'search.html', {'response':L})

def book_preview(request, id):
    response = requests.get('https://www.googleapis.com/books/v1/volumes/'+id+'?key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['volumeInfo']
    return render(request, 'book_preview.html', {'response':response})