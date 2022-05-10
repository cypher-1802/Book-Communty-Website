from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import requests, wikipedia
from .models import Book_User, Read, Discussion, Add_Books


#------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------USER LOGIN-------------------------------------------------------

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
            return error(request, "User not found!!!")

    return render(request, 'login.html')

#------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------USER SIGNUP----------------------------------------------------------

def user_signup(request):
    if request.method == 'POST':

        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if User.objects.filter(username = username).first() is not None:
            return error(request, 'User already exists. Please Login!!!')

        if password == confirm_password:
            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name

            user.save()
            
            u = Book_User(user = user)
            u.to_read_list = ''
            u.library = ''
            u.save()
            
            return redirect('login')

    return render(request, 'signup.html')

def user_logout(request):
    logout(request)
    return redirect('main')

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

def error(request, message):
    return render(request, 'error.html', {'message':message})

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

@login_required(login_url = 'login')
def home(request):

    reader = Book_User.objects.get(user = request.user)

    #Search books
    if request.method == "POST":
        name = request.POST['name']
        return search(request, name)

    #Search among genres
    gnr = "Science Fiction"  #default book

    #fetch from the frontend

    L = genre(gnr, '10', 'newest')

    return render(request, 'home.html', {'reader':reader})

def main(request):
    #Search books
    if request.method == "POST":
        name = request.POST['name']
        return search(request, name)
    #Search among genres
    gnr = "Science Fiction"  #default book

    #fetch from the frontend

    L = genre(gnr, '10', 'newest')
    return render(request, 'Main.html')

def search(request, name):
    #API CALL
    reader = Book_User.objects.get(user = request.user)
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q=intitle:'+name+'&maxResults=12&key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['items']
    L = dict_creator(response)

    return render(request, 'search.html', {'response':L, 'reader':reader})

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

#*************************
def book_preview(request, id):  # renders the book details. Records to_read and library of user and opens discussion forum.

    reader = Book_User.objects.get(user = request.user)

    id = requests.get('https://www.googleapis.com/books/v1/volumes/'+id+'?key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()
    response = id['volumeInfo']

#--------------------------------------About Author---------------------------------------------------------------------------------

    auth = response['authors'][0]
    try:
        result = wikipedia.summary("{}".format(auth))
    except:
        result = wikipedia.summary("{}(Author) ".format(auth))

#--------------------------------------Sorting wrt Genre and Author---------------------------------------------------------------------------------
    try:
        gnr = response['categories'][0]
    except:
        gnr = None

    try:
        s_auth = author(auth, '3', 'relevance')
    except:
        s_auth = None
    try:
        s_genre = genre(gnr, '3', 'relevance')
    except:
        s_genre = None

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
                    
                    data = response['title'] + "**"

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
                return render(request, 'book_preview.html', {'response':response, 'discussion':discussion, 'result':result, 'id':id['id'], 's_genre':s_genre, 's_auth':s_auth, 'reader':reader})

    except:
        pass
    
    return render(request, 'book_preview.html', {'response':response, 'discussion':discussion, 'result':result, 'id':id['id'], 's_genre':s_genre, 's_auth':s_auth, 'reader':reader})

#------------------------------------------------------------------------------------------------------------------------------------
#------------------------------------------------------------------------------------------------------------------------------------

@login_required(login_url = 'login')
def trade(request, id):

#--------------------------------Displays added Books--------------------------------------------------------------------------------

    response = requests.get('https://www.googleapis.com/books/v1/volumes/'+id+'?key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['volumeInfo']

    reader = Book_User.objects.get(user = request.user)

    if request.method == "POST":
        format = request.POST.get('format')
        contact = request.POST.get('contact')
        message = request.POST.get('message')

        add = Add_Books(username = Book_User.objects.get(user = request.user), book_id = id, format = format, contact = contact, message = message)
        add.save()


    if Add_Books.objects.filter(book_id = id).exists():
        add = Add_Books.objects.filter(book_id = id)
        return render(request, 'trade.html', {'add':add, 'id':id, 'response':response, 'reader':reader})

    else:
        return render(request, 'trade.html', {'id':id, 'response':response, 'reader':reader})

#-------------------------------------USER PROFILE-----------------------------------------------------------------------------------

@login_required(login_url = 'login')
def profile(request):
    #pass

    reader = Book_User.objects.get(user = request.user)

    # extracting readlist and collection
    readlist = reader.to_read_list
    collection = reader.library

    L1 = readlist.split("*")   #list of to read books
    L2 = collection.split("*") #list of already read books

    return render(request, 'profile.html', {'reader':reader, 'readlist':L1, 'collection':L2})

    return HttpResponse("hehe")


    # if bio is entered
    # reader.bio = ''#entered value

    # #if photu is uploaded
    # reader.image = ''

    # reader.save()

#---------------------------------------------FOLLOWING------------------------------------------------------------------------------

def following(request, reader):

    reader = Book_User.objects.get(user = request.user)
    f_list = reader.following
    following_list = f_list.split("**")
    
    return following_list

#---------------------------------------------FOLLOWERS------------------------------------------------------------------------------

def following(request, reader):

    reader = Book_User.objects.get(user = request.user)
    f_list = reader.followers
    followers_list = f_list.split("**")
    
    return followers_list
    
    
#----------------------------------------------FOLLOW--------------------------------------------------------------------------------

def follow(request, name):

    reader = Book_User.objects.get(user = request.user)
    reader.following += name + "**"
    reader.save()

#-------------------------------------TRADE PAGE(on search)--------------------------------------------------------------------------

def trd(request):
    if request.method == "POST":
        name = request.POST.get('name')

        response = requests.get('https://www.googleapis.com/books/v1/volumes?q=intitle:'+name+'&maxResults=8&key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['items']
        L = dict_creator(response)

        return render(request, 'trd.html', {'response':L})
    return render(request, "trd.html")

#--------------------------------Displays book by Genre------------------------------------------------------------------------------------
def genre(genre, n, order):
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q=subject:'+genre+'&maxResults='+n+'&orderBy='+order+'&key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['items']
    return dict_creator(response)

#--------------------------------Displays book by Author------------------------------------------------------------------------------------
def author(author, n, order):
    response = requests.get('https://www.googleapis.com/books/v1/volumes?q=inauthor:'+author+'&maxResults='+n+'&orderBy='+order+'&key=AIzaSyC887_T5c9ZEkD9tMzzDB2e_1Dv_5sJ7L0').json()['items']
    return dict_creator(response)

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

def team(request):
    reader = Book_User.objects.get(user = request.user)
    return render(request, 'team.html', {'reader':reader})