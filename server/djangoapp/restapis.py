import requests
import json
import os
from .models import CarDealer, DealerReview
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv


from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

load_dotenv()

# Create a `get_request` to make HTTP GET requests
# e.g., response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
#                                     auth=HTTPBasicAuth('apikey', api_key))
def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        # Call get method of requests library with URL and parameters
        #if api_key:
        #    requests.get(url, headers={'Content-Type': 'application/json'},
        #                    params=kwargs,
        #                    auth=HTTPBasicAuth('apikey', api_key))
        #else:
        response = requests.get(url, headers={'Content-Type': 'application/json'},
                                    params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

# Create a `post_request` to make HTTP POST requests
# e.g., response = requests.post(url, params=kwargs, json=payload)
def post_request(url, json_payload, **kwargs):
    requests.post(url, headers={'Content-Type': 'application/json'},
                        params=kwargs, json=json_payload)
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data


# Create a get_dealers_from_cf method to get dealers from a cloud function
# def get_dealers_from_cf(url, **kwargs):
# - Call get_request() with specified arguments
# - Parse JSON results into a CarDealer object list
def get_dealers_from_cf(url, **kwargs):
    results = []
    # Call get_request with a URL parameter
    json_result = get_request(url)
    if json_result:
        # Get the row list in JSON as dealers
        #print (json_result)
        dealers = json_result["dealerships"]
        # For each dealer object
        for dealer in dealers:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            dealer_obj = CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"],state=dealer["state"])
            results.append(dealer_obj)

    return results

def get_dealer_by_id(url, dealer_id):
    return get_dealers_from_cf(url+"?dealerId="+str(dealerId))

def get_dealer_by_state(url, state):
    return get_dealers_from_cf(url+"?state="+state)


# Create a get_dealer_reviews_from_cf method to get reviews by dealer id from a cloud function
# def get_dealer_by_id_from_cf(url, dealerId):
# - Call get_request() with specified arguments
# - Parse JSON results into a DealerView object list
def get_dealer_reviews_from_cf(url, dealer_id):
    results = []
    # Call get_request with a URL parameter
    new_url = url
    if dealer_id != -1:
        new_url += "?dealerId="+str(dealer_id)

    json_result = get_request(new_url)
    if json_result:
        # Get the row list in JSON as reviews
        #print (json_result)
        reviews = json_result["reviews"]
        # For each review object
        for review in reviews:
            # Get its content in `doc` object
            #dealer_doc = dealer["doc"]
            # Create a CarDealer object with values in `doc` object
            purchase_date = review["purchase_date"] if "purchase_date" in review else None
            car_make = review["car_make"] if "car_make" in review else None
            car_model = review["car_model"] if "car_model" in review else None
            car_year = review["car_year"] if "car_year" in review else None
            sentiment = analyze_review_sentiments(text=review["review"])

            review_obj = DealerReview(dealership=review["dealership"], 
                                        name=review["name"], 
                                        purchase=review["purchase"], 
                                        review=review["review"], 
                                        purchase_date=purchase_date, 
                                        car_make=car_make, 
                                        car_model=car_model, 
                                        car_year=car_year, 
                                        sentiment=sentiment, 
                                        id=review["id"])

            results.append(review_obj)

    return results

# Create an `analyze_review_sentiments` method to call Watson NLU and analyze text
# def analyze_review_sentiments(text):
# - Call get_request() with specified arguments
# - Get the returned sentiment label such as Positive or Negative
def analyze_review_sentiments(**kwargs):
    #load_dotenv()
    api_key = os.environ["nlu_api_key"]
    url = os.environ["nlu_url"]
    #params = dict()
    #params["text"] = kwargs["text"]
    #params["version"] = kwargs["version"]
    #params["features"] = kwargs["features"]
    #params["return_analyzed_text"] = kwargs["return_analyzed_text"]
    #response = requests.get(url, params=params, headers={'Content-Type': 'application/json'},
    #                            auth=HTTPBasicAuth('apikey', api_key))
    #print(response.json)
    #return response.text
    
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2022-04-07',
        authenticator=authenticator)

    natural_language_understanding.set_service_url(url)

    sentiment = "analyzing"
    try:
        response = natural_language_understanding.analyze(
            text=kwargs["text"],
            features=Features(sentiment=SentimentOptions(targets=[kwargs["text"]]))).get_result()
        print(json.dumps(response, indent=2))
        sentiment = response["sentiment"]["document"]["label"]

    except:
        print("Unable to analyze " + kwargs["text"])

    return sentiment