from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer
from .restapis import get_dealers_from_cf, get_dealer_by_id, get_dealer_by_state, get_dealer_reviews_from_cf
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
    context={}
    return render(request, 'djangoapp/about.html', context)
# ...


# Create a `contact` view to return a static contact page
def contact(request):
    context={}
    return render(request, 'djangoapp/contact.html', context)

def navbar(request):
    context={}
    return render(request, 'djangoapp/contact.html', context)

# Create a `login_request` view to handle sign in request
def login_request(request):
    context = {}
    # Handles POST request
    if request.method == "POST":
        # Get username and password from request.POST dictionary
        username = request.POST['username']
        password = request.POST['psw']
        print("{} {}".format(username, password))
             # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        print("Authenticated user {}".format(user))
   
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            print('is auth {} ',user.is_authenticated)
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            return render(request, 'djangoapp:index', context)
    else:
        return render(request, 'djangoapp:index', context)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
   # Get the user object based on session id in request
    print("Log out the user `{}`".format(request.user.username))
    # Logout user in the request
    logout(request)
    # Redirect user back to course list view
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    context = {}
    # If it is a GET request, just render the registration page
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    # If it is a POST request
    elif request.method == 'POST':
        # Get user information from request.POST
        username = request.POST['username']
        password = request.POST['psw']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            # Check if user already exists
            User.objects.get(username=username)
            user_exist = True
        except:
            # If not, simply log this is a new user
            logger.debug("{} is new user".format(username))
        # If it is a new user
        if not user_exist:
            # Create user in auth_user table
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            # Login the user and redirect to course list page
            login(request, user)
            return redirect("djangoapp:index")
        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/ccde7b60-0223-47b0-b34a-f12b6ebf215e/api/dealership.json"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        #dealerships = get_dealer_by_id(url, 15)
        #dealerships = get_dealer_by_state(url, 'Texas')
        # Concat all dealer's short name
        dealer_names = '<br/> '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        return HttpResponse(dealer_names)

# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/ccde7b60-0223-47b0-b34a-f12b6ebf215e/api/review.json"
        # Get reviews for dealer
        reviews = get_dealer_reviews_from_cf(url, dealer_id)
        review_names = '<br/> '.join([ review.name + " for dealer " + 
                str(review.dealership) + " => " + review.review +
                " :: " + review.sentiment for review in reviews])
        # Return a list of reviewer names
        return HttpResponse(review_names)

def test_views(request):
    #return get_dealerships(request)
    return get_dealer_details(request, -1)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

