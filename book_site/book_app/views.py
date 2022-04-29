from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import requests, wikipedia
from .models import Book_User, Read, Discussion, Add_Books, Books


#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

# Create your views here.
def user_login(request):
    if request.method == "POST":

        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return HttpResponse("User not found")#modification required

    return render(request, 'login.html')

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

def user_signup(request):
    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name

            user.save()
            
            u = Book_User(user = user)
            u.save()
            
            return redirect('login')

    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('home')

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

#@login_required(login_url = 'login')
def home(request):
    if request.method == "POST":
        name = request.POST['name']
        return search(request, name)
    return render(request, 'home.html')

def main(request):
    return render(request, 'Main.html')

def search(request, name):
    #API CALL
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q=intitle:'+name+'&key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['items']
    L = dict_creator(response)

    return render(request, 'search.html', {'response':L})

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

def book_preview(request, id):  # renders the book details. Records to_read and library of user and opens discussion forum.

    id = requests.get('https://www.googleapis.com/books/v1/volumes/'+id+'?key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()
    response = id['volumeInfo']

#--------------------------------------About Author---------------------------------------------------------------------------------

    auth = response['authors'][0]
    try:
        result = wikipedia.summary("{}".format(auth))
    except:
        result = wikipedia.summary("{}(Author) ".format(auth))

#--------------------------------Discussion Objects Display-------------------------------------------------------------------------

    discussion = Discussion.objects.filter(book_id = id['id']).order_by("-created_on")[:50]

#--------------------------------Book_User and Read Model----------------------------------------------------------------------------

    #try block for users who are logged in
    try:
        # covers read model, add details to user model also
        if request.method == "POST":

            post = False #default post value
            for key in request.POST:
                if(key == 'message'):
                    post = True
            
            if(post == False):  # run the readlist and library part
                to_read = request.POST.get('status1')
                finished = request.POST.get('status2')

                tr = False
                f = False

                if (to_read is not None) or (finished is not None):
                    
                    data = response['title'] + "*"

                    if to_read is not None:
                        tr = True
                        user_data = Book_User.objects.get(user = request.user)
                        user_data.to_read_list += data
                        user_data.save()

                    # save only those which are not already present,/// delete function too.
                    if finished is not None:
                        f = True
                        user_data = Book_User.objects.get(user = request.user)
                        user_data.library += data
                        user_data.save()

                    #once created next time modify it. below is first time created
                    if Read.objects.filter(username = user_data).exists() == False:
                        st1 = Read.objects.create(username = user_data, book_id = id['id'])
                        st1.save()

                    status = Read.objects.get(book_id = id['id'])
                    status.to_read = tr
                    status.finished = f
                    status.save()

                else:
                    pass

#--------------------------------Discussion Forum------------------------------------------------------------------------------------

            else:
                mess = request.POST.get('mess')
                d = Discussion(username = Book_User.objects.get(user = request.user), book_id = id['id'], message = mess)
                d.save()
                return render(request, 'book_preview.html', {'response':response, 'discussion':discussion, 'result':result, 'id':id['id']})


    except:
        pass
    
    return render(request, 'book_preview.html', {'response':response, 'discussion':discussion, 'result':result, 'id':id['id']})

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

def trade(request, id):

#--------------------------------Displays added Books--------------------------------------------------------------------------------

    if Add_Books.objects.filter(book_id = id).exists():
        add = Add_Books.objects.filter(book_id = id)
        return render(request, 'trade.html', {'add':add, 'id':id})

    else:
        return render(request, 'trade.html', {'id':id})

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

@login_required
def add_books(request, id):

#--------------------------------Opens page for adding books------------------------------------------------------------------------------------

    if request.method == "POST":
        format = request.POST.get('format')
        contact = request.POST.get('contact')
        message = request.POST.get('message')

        add = Add_Books(username = Book_User.objects.get(user = request.user), book_id = id, format = format, contact = contact, message = message)
        add.save()

        return render(request, 'add.html', {'id':id})

    return render(request, 'add.html', {'id':id})

def profile(request):
    pass

def trd(request):
    pass

#--------------------------------Displays book by Genre------------------------------------------------------------------------------------
def genre(genre):
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q=subject:'+genre+'&maxResults=40&orderBy=newest&key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['items']
    L = dict_creator(response)

    return L

#--------------------------------Displays book by Author------------------------------------------------------------------------------------
def author(author):
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q=inauthor:'+author+'&maxResults=40&orderBy=newest&key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['items']
    L = dict_creator(response)

    return L

#--------------------------------Creates dictionary of fields-------------------------------------------------------------------------------
def dict_creator(response):
    L = []

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

    return L