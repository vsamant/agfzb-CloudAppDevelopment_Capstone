from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarDealer
from .restapis import get_dealers_from_cf, get_dealer_by_id, \
        get_dealer_by_state, get_dealer_reviews_from_cf, \
        post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json
import os
from dotenv import load_dotenv

# Get an instance of a logger
logger = logging.getLogger(__name__)
load_dotenv()

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
        print("login as {} {}".format(username, password))
             # Try to check if provide credential can be authenticated
        user = authenticate(username=username, password=password)
        print("Authenticated user {}".format(user))
   
        if user is not None:
            # If user is valid, call login method to login current user
            login(request, user)
            print('is auth {} '.format(user.is_authenticated))
            return redirect('djangoapp:index')
        else:
            # If not, return to login page again
            #return render(request, 'djangoapp:index', context)
            return redirect('djangoapp:index')
    else:
        #return render(request, 'djangoapp:index', context)
        return redirect('djangoapp:index')

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
            print("returning djangoapp:index for user " + user)
            return redirect("djangoapp:index")

        else:
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
def get_dealerships(request):
    context = {}
    if request.method == "GET":
        #url = "https://us-south.functions.appdomain.cloud/api/v1/web/ccde7b60-0223-47b0-b34a-f12b6ebf215e/api/dealership.json"
        url = os.environ["url_get_dealership"]
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        print("Found dealers {}".format(dealerships))
        context = {}
        context["dealership_list"] = dealerships
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
def get_dealer_details(request, dealer_id):
    context = {}
    if request.method == "GET":
        #url = "https://us-south.functions.appdomain.cloud/api/v1/web/ccde7b60-0223-47b0-b34a-f12b6ebf215e/api/review.json"
        url = os.environ["url_get_review"]
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

def index_page(request):
    context = {}
    return render(request, 'djangoapp/index.html', context)

# Create a `add_review` view to submit a review
def add_review(request, dealer_id):
    # TODO check if user is authenticated
    if not request.user.is_authenticated:
        context = {}
        context["error_message"] = "Only authorized users are allowed to access."
        return render(request, 'djangoapp/index.html', context)
            
    url = os.environ["url_post_review"]

    print(request.user)
    ## User is authorized
    review = {}
    review["time"] = datetime.utcnow().isoformat()
    review["dealership"] = dealer_id
    #review["review"] = request.POST["review"]
    review["review"] = "This is a great car dealer"
    review["name"] = request.user.first_name + " " + request.user.last_name
    review["purchase"] = False

    print(review)

    json_payload = {}
    json_payload["review"] = review

    response = post_request(url, json_payload, dealerId=dealer_id)
    context = {}
    context["error_message"] = "Posted review " + response
    return render(request, 'djangoapp/index.html', context)


