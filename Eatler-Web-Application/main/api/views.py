from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from main.models import Restaurant,Product
from django.shortcuts import get_object_or_404
from main.api.serializers import (
    RestaurantSerializer,ProductSerializer,AddressSerializer,NearbyRestaurantSerializer,IntegrationSerializer
    ,OrderSerializer,UserAddressSerializer,DeleteUserAddressSerializer,AddUserAddressSerializer,OrderHistorySerializer,
    ChatbotUrlSerializer,PaymentStatusSerializer,OrderStatusSerializer,CancelOrderStatusSerializer,BookTableSerializer,
    FeedbackSerializer,RestaurantFromCitySerializer)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.authtoken.models import Token
import json
from django.http import JsonResponse,HttpResponse
from django.forms.models import model_to_dict
import requests
from geopy.geocoders import Nominatim
from math import cos, asin, sqrt, pi
from geopy.exc import GeocoderTimedOut
import os
import dialogflow_v2beta1 as dialogflow
from google.api_core.exceptions import InvalidArgument
import uuid
import cgi
from datetime import date,datetime,timedelta
from django.utils import timezone
from main.models import User,Restaurant,Order,Address,Issues,BookTable,Feedback
from main.paytm import Checksum
MERCHANT_KEY = '!mEIW7_rQ@awJKtL'
from django.core import serializers
from Eatler.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
import pandas as pd 



class getQuery(CreateAPIView):
    serializer_class = RestaurantSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
            query = serializer.validated_data['query']
            print(query)
            restaurant_list=Restaurant.objects.raw(query)
            # print(restaurant_list)
            # dict={}
            # for object in restaurant_list:
            #     # dict[object.name] = []  # converts ValuesQuerySet into Python list
            #     # dict[object.name]={'city':object.city,'address':object.address,'photo':object.photo,'description':object.description,'email':object.email,'contact_number':object.contact_number}
            dict1={}
            i=0
            for object in restaurant_list:
                url='http://127.0.0.1:8000/media/'+str(object.photo)
                dict1[i]={'name':object.name,'city':object.city,'address':object.address,'short_description':object.short_description,'long_description':object.long_description,'email':object.email,'contact_number':object.contact_number,
                            'open_time':object.open_time,'close_time':object.close_time,'photo_url':url,'northindian':object.northindian,
                            'southindian':object.southindian,'chinese':object.chinese,'continental':object.continental,
                            'oriental':object.oriental,'veg':object.veg,'non_veg':object.non_veg,'live_video':object.live_video}
                i=i+1
            print(dict1)
            return Response(dict1)




class getProduct_with_param(CreateAPIView):
    serializer_class = ProductSerializer
    def get(self, request, format=None):
        restaurant = request.query_params['restaurant']
        restaurantID=Restaurant.objects.filter(name=restaurant).first()
        product=Product.objects.filter(restaurant=restaurantID)
        dict1={}
        i=0
        for object in product:
            url='http://127.0.0.1:8000/media/'+str(object.photo)

            dict1[object.pk]={'name':object.name,'short_description':object.short_description,'long_description':object.long_description,'price':object.price,'photo_url':url,
                        'add_on1':object.add_on1,'add_on2':object.add_on2,'add_on3':object.add_on3,'add_on4':object.add_on4,
                        'add_on5':object.add_on5,'type':object.type,'cuisine':object.cuisine,'category':object.category,'rating':object.rating}
        return Response(dict1)



class getProduct_without_param(CreateAPIView):
    serializer_class = ProductSerializer
    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
            restaurant = serializer.validated_data['restaurant']

            print(restaurant)
            restaurantID=Restaurant.objects.filter(name=restaurant).first()
            print(restaurantID)
            product=Product.objects.filter(restaurant=restaurantID)
            dict1={}
            for object in product:
                url='http://127.0.0.1:8000/media/'+str(object.photo)
                dict1[object.pk]={'name':object.name,'short_description':object.short_description,'long_description':object.long_description,'price':object.price,'photo_url':url,
                            'add_on1':object.add_on1,'add_on2':object.add_on2,'add_on3':object.add_on3,'add_on4':object.add_on4,
                            'add_on5':object.add_on5,'type':object.type,'cuisine':object.cuisine,'category':object.category,
                            'rating':object.rating,}
            return Response(dict1)

class getProduct_without_param_android(CreateAPIView):
    serializer_class = ProductSerializer
    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
            restaurant = serializer.validated_data['restaurant']

            print(restaurant)
            restaurantID=Restaurant.objects.filter(name=restaurant).first()
            print(restaurantID)
            product=Product.objects.filter(restaurant=restaurantID)
            dict1={}
            i=0
            for object in product:
                url='http://127.0.0.1:8000/media/'+str(object.photo)
                dict1[i]={'product_id':object.pk,'name':object.name,'short_description':object.short_description,'long_description':object.long_description,'price':object.price,'photo_url':url,
                            'add_on1':object.add_on1,'add_on2':object.add_on2,'add_on3':object.add_on3,'add_on4':object.add_on4,
                            'add_on5':object.add_on5,'type':object.type,'cuisine':object.cuisine,'category':object.category,
                            'rating':object.rating}
                i=i+1
            return Response(dict1)

class getCoordinates(CreateAPIView):
    serializer_class = AddressSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
            address = serializer.validated_data['address']
            geolocator = Nominatim(user_agent="main")
            try:
                location = geolocator.geocode(address,timeout=None)
            except GeocoderTimedOut as e:
                response={'Problem':"Network Issues",'status':"failed"}
                return Response(response)
            response={'latitude':location.latitude,'longitude':location.longitude}
            return Response(response)


def do_geocode(address,geolocator, attempt=1, max_attempts=5):
    try:
        return geolocator.geocode(address)
    except GeocoderTimedOut:
        if attempt <= max_attempts:
            return do_geocode(address,geolocator, attempt=attempt+1)
        response={'Problem':"Network Issues",'status':"failed"}
        return Response(response)

class getNearbyRestaurant_with_param(CreateAPIView):
    def distance(self,lat1, lon1, lat2, lon2):
        p = pi/180
        a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
        return 12742 * asin(sqrt(a))

    serializer_class=NearbyRestaurantSerializer
    def get(self,request,format=None):
        address=request.query_params['address']
        city=request.query_params['city']
        response={}
        geolocator = Nominatim(user_agent="main")
        location=do_geocode(address,geolocator)
        restaurant=Restaurant.objects.filter(city=city)
        i=0
        for object in restaurant:
            dist=self.distance(location.latitude,location.longitude,object.latitude,object.longitude)
            if(dist<=5):
                url='http://127.0.0.1:8000/media/'+str(object.photo)
                response[i]={'distance':dist,'name':object.name,'city':object.city,'address':object.address,
                            'short_description':object.short_description,'long_description':object.long_description,
                            'email':object.email,'contact_number':object.contact_number,'open_time':object.open_time,
                            'close_time':object.close_time,'photo_url':url,'northindian':object.northindian,
                            'southindian':object.southindian,'chinese':object.chinese,'continental':object.continental,
                            'oriental':object.oriental,'veg':object.veg,'non_veg':object.non_veg,'live_video':object.live_video}
                i=i+1
        if response=={}:
            response={'status':"Not Found"}
            return Response(response)
        response['status']='success'
        return Response(response)



class getNearbyRestaurant_without_param(CreateAPIView):
    def distance(self,lat1, lon1, lat2, lon2):
        p = pi/180
        a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
        return 12742 * asin(sqrt(a))

    serializer_class=NearbyRestaurantSerializer
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            address = serializer.validated_data['address']
            city = serializer.validated_data['city']
            response={}
            geolocator = Nominatim(user_agent="main")
            location=self.do_geocode(address,geolocator)
            restaurant=Restaurant.objects.filter(city=city)
            i=0
            for object in restaurant:
                dist=self.distance(location.latitude,location.longitude,object.latitude,object.longitude)
                if(dist<=5):
                    url='http://127.0.0.1:8000/media/'+str(object.photo)
                    response[i]={'distance':dist,'name':object.name,'city':object.city,'address':object.address,'locality':object.locality,
                                'short_description':object.short_description,'long_description':object.long_description,'email':object.email,
                                'contact_number':object.contact_number,'open_time':object.open_time,'close_time':object.close_time,'photo_url':url,
                                'northindian':object.northindian,'southindian':object.southindian,'chinese':object.chinese,'continental':object.continental,'oriental':object.oriental,
                                'veg':object.veg,'non_veg':object.non_veg,'live_video':object.live_video}
                    i=i+1
            if response=={}:
                response={'status':"Not Found"}
            return Response(response)

    def do_geocode(self,address,geolocator, attempt=1, max_attempts=5):
        try:
            return geolocator.geocode(address)
        except GeocoderTimedOut:
            if attempt <= max_attempts:
                return self.do_geocode(address,geolocator, attempt=attempt+1,max_attempts=5)
            response={'Problem':"Network Issues",'status':"failed"}
            return Response(response)




data_table = pd.DataFrame(
    columns=['SessionId', 'gintent', 'how', 'locality', 'city', 'restaurant', 'rest_cat', 'food_list', 'food_info',
             'itemsjson','order_day','order_time'])

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class chatbot_integration_API(CreateAPIView):
    serializer_class = IntegrationSerializer
    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
            text_to_be_analyzed = serializer.validated_data['message']
            user_name=serializer.validated_data['user_name']
            print(text_to_be_analyzed)
            global data_table
            sessionid = get_client_ip(request)
            flag = 0
            for id in data_table['SessionId']:
                if id == sessionid:
                    flag = 1
            if flag == 0:
                data_table = data_table.append(
                    {'SessionId': sessionid, 'gintent': None, 'how': None, 'locality': None, 'city': None,
                     'restaurant': None,
                     'rest_cat': {}, 'food_list': {}, 'food_info': {},
                     'itemsjson': {},'order_day':datetime.now().date(),'order_time':datetime.now().time()}, ignore_index=True)
            response_data = detect_intent(text_to_be_analyzed, user_name, sessionid)
            return Response(response_data)

def detect_intent(text_to_be_analyzed, user, sessionid):
    global data_table
    os.environ[
        "GOOGLE_APPLICATION_CREDENTIALS"] = 'main/authentication/eatler-web-ywksta-c938ecbc544e.json'  # [path] of eatler-tgdjdx-3ab8e4382f8f.json
    DIALOGFLOW_PROJECT_ID = 'eatler-web-ywksta'
    DIALOGFLOW_LANGUAGE_CODE = 'en'
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, sessionid)
    text_input = dialogflow.types.TextInput(text=text_to_be_analyzed, language_code=DIALOGFLOW_LANGUAGE_CODE)
    query_input = dialogflow.types.QueryInput(text=text_input)
    try:
        response = session_client.detect_intent(session=session, query_input=query_input)
    except InvalidArgument:
        raise

    reply = response.query_result.fulfillment_text
    reply = {'text': reply, 'Buttons': []}
    intent = response.query_result.intent.display_name
    text = reply['text']
    url = ''
    Buttons = []
    card_rest = []
    card_product = []
    paydet = {}
    if intent == 'Welcome Intent' or intent == 'chatbot_active':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                data_table.at[i, 'gintent'] = None
                data_table.at[i, 'how'] = None
                data_table.at[i, 'locality'] = None
                data_table.at[i, 'city'] = None
                data_table.at[i, 'restaurant'] = None
                data_table.at[i, 'rest_cat'] = {}
                data_table.at[i, 'food_list'] = {}
                data_table.at[i, 'food_info'] = {}
                data_table.at[i, 'itemsjson'] = {}
                data_table.at[i,'order_day']='0'
                data_table.at[i, 'order_time'] = '0'
                break
        if user != '':
            text = random.choice([
                                     'Hi ' + user + '! I see you have great taste coming to the world\'s first transparent kitchen. I am Vafer, your virtual waiter. How would you like my assistance today?',
                                     'Hey ' + user + '! How are you doing today? I am Vafer, your virtual waiter and aid. How may I help you today?',
                                     'Hey there ' + user + '! Great choice entering the world\'s first transparent eatery. I am Vafer, your virtual waiter. Any way I can help you today?',
                                     'Hello ' + user + '! Welcome to the world\'s first transparent eatery. I am Vafer, your virtual waiter. How may I assist you today?'])
        Buttons = ['Order food 🍔', 'Book a table 🍽', 'Let\'s Talk 💬']
    elif intent == 'Order':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                data_table.at[i, 'gintent'] = 'Order'
                data_table.at[i, 'how'] = None
                data_table.at[i, 'locality'] = None
                data_table.at[i, 'city'] = None
                data_table.at[i, 'restaurant'] = None
                data_table.at[i, 'rest_cat'] = {}
                data_table.at[i, 'food_list'] = {}
                data_table.at[i, 'food_info'] = {}
                data_table.at[i, 'itemsjson'] = {}
                data_table.at[i, 'order_day'] = '0'
                data_table.at[i, 'order_time'] = '0'
                break
        Buttons = ['Delivery 🛵', 'Carry Out 🥡']
    elif intent == 'Order.Delivery':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                data_table.at[i, 'gintent'] = 'Order'
                data_table.at[i, 'how'] = 'd'
                data_table.at[i, 'locality'] = None
                data_table.at[i, 'city'] = None
                data_table.at[i, 'restaurant'] = None
                data_table.at[i, 'rest_cat'] = {}
                data_table.at[i, 'food_list'] = {}
                data_table.at[i, 'food_info'] = {}
                data_table.at[i, 'itemsjson'] = {}
                data_table.at[i, 'order_day'] = '0'
                data_table.at[i, 'order_time'] = '0'
                break
    elif intent == 'order.takeaway':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                data_table.at[i, 'gintent'] = 'Order'
                data_table.at[i, 'how'] = 't'
                data_table.at[i, 'locality'] = None
                data_table.at[i, 'city'] = None
                data_table.at[i, 'restaurant'] = None
                data_table.at[i, 'rest_cat'] = {}
                data_table.at[i, 'food_list'] = {}
                data_table.at[i, 'food_info'] = {}
                data_table.at[i, 'itemsjson'] = {}
                data_table.at[i, 'order_day'] = '0'
                data_table.at[i, 'order_time'] ='0'
                break
    elif intent == 'Order.address':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                how = data_table['how'][i]
                if data_table['locality'][i] is None and data_table['city'][i] is None:
                    locality = response.query_result.parameters.fields['Locality'].string_value
                    city = response.query_result.parameters.fields['City'].string_value
                    data_table.at[i, 'locality'] = locality
                    data_table.at[i, 'city'] = city
                    break
                else:
                    locality=data_table['locality'][i]
                    city=data_table['city'][i]
        add_request = requests.get(
            'http://127.0.0.1:8000/main_api/nearbyRestaurant_get/?address=' + locality + ' ' + city + '&city=' + city)
        add_request = add_request.json()
        current_time = datetime.now().time()
        rest_cat = {}
        if add_request['status'] == 'success':
            if how == 'd':
                text = 'Here are the restaurants nearest to your location that are currently open and are available for delivery.\n'
            elif how == 't':
                text = 'Here are the restaurants nearest to your location that are currently open.\n'
            for key in add_request:
                if key != 'status':
                    cat_list = ['Dessert 🍰', 'Sweet🍯', 'Snacks🍟']
                    open_time = datetime.strptime(add_request[key]['open_time'], '%H:%M:%S').time()
                    close_time = datetime.strptime(add_request[key]['close_time'], '%H:%M:%S').time()
                    #if open_time < current_time and current_time < close_time:
                    if add_request[key]['northindian'] == True:
                        cat_list.append('North Indian🍗')
                    if add_request[key]['southindian'] == True:
                        cat_list.append('South Indian🍚')
                    if add_request[key]['chinese'] == True:
                        cat_list.append('Chinese🍜')
                    if add_request[key]['continental'] == True:
                        cat_list.append('Continental 🥗')
                    if add_request[key]['oriental'] == True:
                        cat_list.append('Oriental 🥟')
                    rest_cat.update({add_request[key]['name']: cat_list})
                    card_rest.append({'title': add_request[key]['name'],
                                      'description': 'Address: ' + add_request[key]['address'] + '\nContact: ' + str(
                                          add_request[key]['contact_number']) + '\nOpen: ' + str(add_request[key][
                                                                                                     'open_time']) + '-' + str(
                                          add_request[key]['close_time']),
                                      'imgurl': add_request[key]['photo_url']})
            for i in data_table.index:
                if data_table['SessionId'][i] == sessionid:
                    data_table.at[i, 'rest_cat'] = rest_cat
                    break
        else:
            text='I am afraid we don\'t have an outlet nearby.Try again with another address📍'
    elif intent == 'Order.restaurants':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                if data_table['restaurant'][i] is None:
                    restaurant = response.query_result.parameters.fields['restaurants'].string_value
                    data_table.at[i, 'restaurant'] = restaurant
                    data_table.at[i, 'food_list'] = {}
                    data_table.at[i, 'food_info'] = {}
                    data_table.at[i, 'itemsjson'] = {}
                else:
                    restaurant=data_table['restaurant'][i]
                text='Available Categories at ' + restaurant + ':'
                for cat in data_table['rest_cat'][i][data_table['restaurant'][i]]:
                    Buttons.append(cat)
                break
    elif intent == 'category_choose':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                if data_table['gintent'][i] is None:
                    text='First you\'ll have to choose between Ordering out or Booking a table.'
                    break
                elif data_table['how'][i] is None:
                    text = 'But would you like a delivery or carry out?'
                    break
                elif data_table['locality'][i] is None or data_table['city'][i] is None:
                    if data_table['how'][i]=='d':
                        text = 'But first let us know where you want your delivery at?'
                        break
                    elif data_table['how'][i]=='t':
                        text = 'But first let us know the nearest location for your takeaway.'
                        break
                elif data_table['restaurant'][i] is None:
                    text = 'We would like you to first choose a restaurant.'
                    break
                else:
                    restaurant_chosen = data_table['restaurant'][i]
                    category=response.query_result.parameters.fields['category'].string_value
                    text='Here are some ' + category + ' Dishes:\nYou can place your order altogether or you can order individually'
                    prod_request = requests.get('http://127.0.0.1:8000/main_api/product_get/?restaurant=' + restaurant_chosen)
                    prod_request = prod_request.json()
                    food_info = {}
                    for key in prod_request:
                        addons = []
                        if prod_request[key]['add_on1'] != '':
                            addons.append(prod_request[key]['add_on1'])
                        if prod_request[key]['add_on2'] != '':
                            addons.append(prod_request[key]['add_on2'])
                        if prod_request[key]['add_on3'] != '':
                            addons.append(prod_request[key]['add_on3'])
                        if prod_request[key]['add_on4'] != '':
                            addons.append(prod_request[key]['add_on4'])
                        if prod_request[key]['add_on5'] != '':
                            addons.append(prod_request[key]['add_on5'])
                        food_info.update(
                            {prod_request[key]['name']: {'id': key, 'addons': addons, 'price': prod_request[key]['price']}})
                        if prod_request[key]['cuisine'] == category or prod_request[key]['type'] == category or prod_request[key][
                            'category'] == category:
                            card_product.append({'title': prod_request[key]['name'],
                                                  'description': 'Rs.' + str(prod_request[key]['price']) + '\n' + 'Type:' + prod_request[key][
                                        'type'] + '\n' + 'Cuisine:' + prod_request[key]['cuisine'],
                                                  'imgurl':prod_request[key]['photo_url']})
                    data_table.at[i, 'food_info'] = food_info
                    Buttons=['I am Done']
                    break
    elif intent=='food_choose':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                if data_table['gintent'][i] is None:
                    text = 'First you\'ll have to choose between Ordering out or Booking a table.'
                    break
                elif data_table['how'][i] is None:
                    text = 'But would you like a delivery or carry out?'
                    break
                elif data_table['locality'][i] is None or data_table['city'][i] is None:
                    if data_table['how'][i] == 'd':
                        text = 'But first let us know where you want your delivery at?'
                        break
                    elif data_table['how'][i] == 't':
                        text = 'But first let us know the nearest location for your takeaway.'
                        break
                elif data_table['restaurant'][i] is None:
                    text = 'We would like you to first choose a restaurant.'
                    break
                else:
                    text = 'Added '
                    if len(data_table['food_list'][i]) == 0:
                        for j in range(len(response.query_result.parameters.fields['food_items'].list_value)):
                            data_table['food_list'][i].update(
                                {response.query_result.parameters.fields['food_items'].list_value[j]:
                                     int(response.query_result.parameters.fields['number'].list_value[j])})
                            text+=str(int(response.query_result.parameters.fields['number'].list_value[j]))+' '+response.query_result.parameters.fields['food_items'].list_value[j]+','
                    else:
                        for key in response.query_result.parameters.fields:
                            if key == 'food_items':
                                for j in range(len(response.query_result.parameters.fields['food_items'].list_value)):
                                    flag = 0
                                    for item in data_table['food_list'][i]:
                                        if item == response.query_result.parameters.fields['food_items'].list_value[j]:
                                            new_qty = int(data_table['food_list'][i][item]) + int(
                                                response.query_result.parameters.fields['number'].list_value[j])
                                            data_table['food_list'][i].update({item: new_qty})
                                            flag = 1
                                    if flag == 0:
                                        data_table['food_list'][i].update(
                                            {response.query_result.parameters.fields['food_items'].list_value[j]: int(
                                                response.query_result.parameters.fields['number'].list_value[j])})
                                    text+=str(int(response.query_result.parameters.fields['number'].list_value[j]))+' '+response.query_result.parameters.fields['food_items'].list_value[j]+','
                    text += ' to cart'
                    break
    elif intent == 'remove_item':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                if data_table['gintent'][i] is None:
                    text = 'First you\'ll have to choose between Ordering out or Booking a table.'
                    break
                elif data_table['how'][i] is None:
                    text = 'But would you like a delivery or carry out?'
                    break
                elif data_table['locality'][i] is None or data_table['city'][i] is None:
                    if data_table['how'][i] == 'd':
                        text = 'But first let us know where you want your delivery at?'
                        break
                    elif data_table['how'][i] == 't':
                        text = 'But first let us know the nearest location for your takeaway.'
                        break
                elif data_table['restaurant'][i] is None:
                    text = 'We would like you to first choose a restaurant.'
                    break
                elif not bool(data_table['food_list'][i]):
                    text = 'Your cart is already empty'
                    break
                else:
                    remove_item = response.query_result.parameters.fields['food_items'].string_value
                    remove_quantity = response.query_result.parameters.fields['number'].number_value
                    for key in data_table['food_list'][i]:
                        if key == remove_item:
                            data_table['food_list'][i][key] -= int(remove_quantity)
                            if data_table['food_list'][i][key] ==0:
                                text='Removed '+remove_item+' from your cart'
                                break
                            elif data_table['food_list'][i][key]<0:
                                text=remove_item+' is already removed from your cart'
                                break
                            else:
                                text='Removed '+str(int(remove_quantity))+' '+remove_item+' from your cart'
                                break
                    break
    elif intent=='Show_cart':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                for item_key in data_table['food_list'][i]:
                    if data_table['food_list'][i][item_key] <= 0:
                        data_table['food_list'][i] = {key: val for key, val in data_table['food_list'][i].items() if
                                                      key != item_key}
                if len(data_table['food_list'][i]) != 0:
                    text='Your cart have:\n'
                    for key in data_table['food_list'][i]:
                        for item in data_table['food_info'][i]:
                            if item == key:
                                data_table['itemsjson'][i].update({data_table['food_info'][i][item]['id']: [
                                    data_table['food_list'][i][key], key,
                                    str(int(data_table['food_info'][i][item]['price']))]})
                        text+=str(int(data_table['food_list'][i][key])) + ' ' + key+'\n'
                    text+='Do you need any add ons?'
                    Buttons=['Yes','No']
                else:
                    text='Your cart is currently empty.'
                    Buttons=['Add Items']
                break
    elif intent == 'Show_cart - no':
        addon1 = ''
        addon2 = ''
        addon3 = ''
        addon4 = ''
        addon5 = ''
        for i in data_table.index:
            if data_table['SessionId'][i]==sessionid:
                for key in data_table['itemsjson'][i]:
                    data_table['itemsjson'][i][key].append(addon1)
                    data_table['itemsjson'][i][key].append(addon2)
                    data_table['itemsjson'][i][key].append(addon3)
                    data_table['itemsjson'][i][key].append(addon4)
                    data_table['itemsjson'][i][key].append(addon5)
                break
        text='Shall we schedule your order?'
        Buttons=['Yes','No']
    elif intent == 'Show_cart - yes':
        text='From the following options, provide the add ons in the given format:\n'
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                for key in data_table['food_list'][i]:
                    show_addons = ''
                    for item in data_table['food_info'][i]:
                        if item == key:
                            for addon in data_table['food_info'][i][item]['addons']:
                                show_addons = show_addons + addon + ', '
                    text+=key + ': ' + show_addons + '\n'
                break
    elif intent == 'Addons':
        for i in data_table.index:
            if data_table['SessionId'][i] == sessionid:
                for j in range(len(response.query_result.parameters.fields['food_items'].list_value)):
                    addon1 = ''
                    addon2 = ''
                    addon3 = ''
                    addon4 = ''
                    addon5 = ''
                    for key in data_table['itemsjson'][i]:
                        if data_table['itemsjson'][i][key][1] == response.query_result.parameters.fields['food_items'].list_value[j]:
                            if i < len(response.query_result.parameters.fields['addons'].list_value):
                                addon1 = response.query_result.parameters.fields['addons'].list_value[j]
                                #print(addon1)
                            if i < len(response.query_result.parameters.fields['addons1'].list_value):
                                addon2 = response.query_result.parameters.fields['addons1'].list_value[j]
                                #print(addon2)
                            if i < len(response.query_result.parameters.fields['addons2'].list_value):
                                addon3 = response.query_result.parameters.fields['addons2'].list_value[j]
                                #print(addon3)
                            if i < len(response.query_result.parameters.fields['addons3'].list_value):
                                addon4 = response.query_result.parameters.fields['addons3'].list_value[j]
                            if i < len(response.query_result.parameters.fields['addons4'].list_value):
                                addon5 = response.query_result.parameters.fields['addons4'].list_value[j]
                            data_table['itemsjson'][i][key].append(addon1)
                            data_table['itemsjson'][i][key].append(addon2)
                            data_table['itemsjson'][i][key].append(addon3)
                            data_table['itemsjson'][i][key].append(addon4)
                            data_table['itemsjson'][i][key].append(addon5)
                break
        text='Shall we schedule your order?'
        Buttons=['Yes','No']
    elif intent=='Show_cart - no - yes':
        for i in data_table.index:
            if data_table['SessionId'][i]==sessionid:
                data_table.at[i,'how']='s'+data_table['how'][i]
        text='So when do you want to schedule your order?'
        current_time = datetime.now().time()
        if current_time < datetime.strptime('23:00:00', '%H:%M:%S').time():
            Buttons=['Today','Tomorrow','Day after tomorrow']
        else:
            Buttons = ['Tomorrow', 'Day after tomorrow']
    elif intent=='Show_cart - no - no':
        text='I see you are done. Let\'s checkout?'
        Buttons=['Checkout']
    elif intent=='Addons - yes':
        for i in data_table.index:
            if data_table['SessionId'][i]==sessionid:
                data_table.at[i,'how']='s'+data_table['how'][i]
        text='So when do you want to schedule your order?'
        current_time = datetime.now().time()
        if current_time < datetime.strptime('23:00:00', '%H:%M:%S').time():
            Buttons = ['Today', 'Tomorrow', 'Day after tomorrow']
        else:
            Buttons = ['Tomorrow', 'Day after tomorrow']
    elif intent=='Addons - no':
        text='I see you are done. Let\'s checkout?'
        Buttons = ['Checkout']
    elif intent=='Schedule':
        order_day=response.query_result.parameters.fields['date-time'].string_value
        order_day=datetime.strptime(order_day,'%Y-%m-%dT%I:%M:%S%z').date()
        current_day=datetime.now().date()
        current_time=datetime.now().time()
        three_days_after=(datetime.now()+timedelta(days=3)).date()
        if current_day==order_day and current_time>datetime.strptime('23:00:00', '%H:%M:%S').time():
            text='Delivery/takeaway will not be available at this hour'
        elif order_day>three_days_after:
            text='We can only provide delivery/takeaway within 2 days from now'
        else:
            for i in data_table.index:
                if data_table['SessionId'][i]==sessionid:
                    data_table.at[i,'order_day']=order_day
                    break
            text='Enter any time between 9 AM and 11 PM'
    elif intent=='Schedule.time':
        order_time=response.query_result.parameters.fields['time'].string_value
        #print(order_time)
        order_time=datetime.strptime(order_time,'%Y-%m-%dT%H:%M:%S%z').time()
        #print(order_time)
        if order_time>datetime.strptime('23:00:00', '%H:%M:%S').time() or order_time<datetime.strptime('09:00:00', '%H:%M:%S').time():
            text='Oops! I am afraid we are not available at this hour'
        elif order_time<(datetime.now()+timedelta(minutes=50)).time():
            text='We cannot provide a healthy meal in such a short time.'
        else:
            for i in data_table.index:
                if data_table['SessionId'][i]==sessionid:
                    data_table.at[i,'order_time']=order_time
                    break
            text = 'I see you are done. Let\'s checkout?'
            Buttons=['Checkout']
    elif intent=='Checkout':
        for i in data_table.index:
            if data_table['SessionId'][i]==sessionid:
                itemsjson=data_table['itemsjson'][i]
                tot_price=0
                for key in itemsjson:
                    tot_price+=int(itemsjson[key][2])
                rest_name=data_table['restaurant'][i]
                order_day=data_table['order_day'][i]
                order_time=data_table['order_time'][i]
                how=data_table['how'][i]
                break
        url='switch to payment'
        paydet = {'itemsjson': str(itemsjson),
                  'total_price': int(tot_price),
                  'restaurant_name': rest_name,
                  'order_date': order_day,
                  'order_time': order_time,
                  'how':how}
    elif intent=='Book':
        url='switch to Book a table'
    elif intent=='recent_order':
        url='switch to order history'
    elif intent=='Let\'sTalk':
        Buttons=['Browse more about us 🌐','Give a feedback ⭐','Have a small talk💬']
    elif intent=='Knowus':
        Buttons=['Our Mission ⚔','Our Vision👀','Who are we 👤','What we do❓','How we do it💪🏼']
    elif intent=='feedback':
        Buttons=['Technical','Delivery Related','Food','Restaurant','Health and Hygiene','Overall Experience']
    elif intent == 'feedback.category - custom':
        feedback_text = response.query_result.query_text
        print(feedback_text)
        feedback_cat=response.query_result.parameters.fields['feedback_category'].string_value
        print(feedback_cat)
        url='127.0.0.1:5000/predict' #Chatbot webhook url + '/predict'
        response = requests.post(url, data=json.dumps(feedback_text),headers={'Content-Type': 'application/json'})
        response=response.json()
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        nature = response['prediction']
        print(nature)
        feedback_req = requests.get(
            'http://127.0.0.1:8000/main_api/getFeedback/?message=' + feedback_text + '&category=' + feedback_cat + '&fb_type=' + nature)
        print(feedback_req)
    elif intent=='Get.data.details':
        #__get__data__
        data_table.to_csv('Chatbot_data_for_analysis.csv')
        return {'fulfillmentText':'Your data have been downloaded'}
    reply = {'text': text,
             'Buttons': Buttons,
             'url': url,
             'card_restaurant': card_rest,
             'card_product': card_product
             }

    response_data = {'reply': reply, 'intent': intent,'payment_details':paydet}
    return response_data








            
class OrderDetails(CreateAPIView):
    serializer_class = OrderSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
            user_phone_number = serializer.validated_data['user_phone_number']
            restaurant_name=serializer.validated_data['restaurant']
            phone_number=serializer.validated_data['phone_number']
            item_jsons=serializer.validated_data['item_jsons']
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            shipping_address = serializer.validated_data['shipping_address']
            billing_address = serializer.validated_data['billing_address']
            state = serializer.validated_data['state']
            country = serializer.validated_data['country']
            zip_code = serializer.validated_data['zip_code']
            total_price=serializer.validated_data['total_price']
            paymentStatus=serializer.validated_data['paymentStatus']
            how=serializer.validated_data['how']
            special_instruction=serializer.validated_data['special_instruction']
            schedule_time=serializer.validated_data['schedule_time']
            schedule_date=serializer.validated_data['schedule_date']
            try:
                user=User.objects.filter(phone_number=user_phone_number)[0]
            except:
                user=None
            response_data={}
            if user:
                try:
                    restaurant=Restaurant.objects.filter(name=restaurant_name)[0]
                except:
                    restaurant=None
                

                if restaurant:
                    if how=='d':
                        how='delivery'
                    elif how=='t':
                        how='takeaway'
                    elif how=='sd':
                        how='schedule-delivery'
                    elif how=='st':
                        how='schedule-takeaway'


                    if how=="delivery" or how=="takeaway":
                        today=date.today()
                        schedule_date=today.strftime("%Y-%m-%d")
                        now = datetime.now()
                        schedule_time=now.strftime("%H:%M:%S")

                    if how=='delivery' or how=='schedule-delivery':
                        order=Order(user=user,restaurant=restaurant,item_jsons=item_jsons,name=name,phone_number=phone_number,email=email,
                                    shipping_address=shipping_address,billing_address=billing_address,state=state,country=country,zip_code=zip_code,
                                    total_price=total_price,payment_mode=paymentStatus,how=how,special_instruction=special_instruction,schedule_time=schedule_time,
                                    schedule_date=schedule_date)

                    else:
                        order=Order(user=user,restaurant=restaurant,item_jsons=item_jsons,name=name,phone_number=phone_number,email=email,
                                    total_price=total_price,payment_mode=paymentStatus,how=how,special_instruction=special_instruction,schedule_time=schedule_time,
                                    schedule_date=schedule_date)
                   
                    order.save()
                    id=order.order_id
                    if paymentStatus=="COD":
                        order.order_status='pending'
                        order.payment_mode='COD'
                        order.payment_status=False
                        order.save()
                        if how=='delivery' or how=='schedule-delivery':
                            newadd=shipping_address+'\n'+state+'\n'+country+'\n'+zip_code
                            obj=Address.objects.filter(user=user,address=newadd)
                            if obj.count()<=0:
                                address=Address(user=user,address=newadd)
                                address.save()
                            
                            
                        response={'order_id':id,'status':'success','checkSum':""}
                        return Response(response)

                    else:
                        order.save()
                        if how=='delivery' or how=='schedule-delivery':
                            newadd=shipping_address+'\n'+state+'\n'+country+'\n'+zip_code
                            obj=Address.objects.filter(user=user,address=newadd)
                            if obj.count()<=0:
                                address=Address(user=user,address=newadd)
                                address.save()
                        id=order.order_id
                        data_dict = {
                            'MID':'aVrRqW70498541104158',
                            'ORDER_ID':str(order.order_id),
                            'TXN_AMOUNT':str(order.total_price),
                            'CUST_ID':str(email),
                            'INDUSTRY_TYPE_ID':'Retail',
                            'WEBSITE':'WEBSTAGING',
                            'CHANNEL_ID':'WAP',
                            'CALLBACK_URL':'https://securegw-stage.paytm.in/theia/paytmCallback?ORDER_ID='+str(order.order_id),
                        }
                        data_dict['CHECKSUMHASH']=Checksum.generate_checksum(data_dict,MERCHANT_KEY)
                        print(data_dict['CHECKSUMHASH'])
                        response={'order_id':id,'status':'success','checkSum':data_dict['CHECKSUMHASH']}
                        return Response(response)



                else:
                    response_data={'status':'restaurant not found'}
                    return Response(response_data)

            else:
                response_data={'status':'user not found'}
                return Response(response_data)
        else:
            return Response({'status':"Fail"})



class getPaymentStatus(CreateAPIView):
    serializer_class = PaymentStatusSerializer


    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data,)
        if serializer.is_valid():
            order_id=serializer.validated_data['order_id']
            payment_mode=serializer.validated_data['payment_mode']
            paymentStatus=serializer.validated_data['payment_status']
            
            order=Order.objects.filter(order_id=order_id)
            if order.count()<=0:
                response={'detail':'invalid order id','success':'False'}
                return Response(response)
            else:
                order=order.first()
                order.payment_mode=payment_mode
                if paymentStatus=="success":
                    order.payment_status=True
                    order.order_status='pending'
                    order.save()
                else:
                    order.payment_status=False
                    order.save()
                response={'order_status':order.order_status,'success':'True'}
                return Response(response)


class getOrderStatus(CreateAPIView):
    serializer_class = OrderStatusSerializer


    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data,)
        if serializer.is_valid():
            order_id=serializer.validated_data['order_id']
            
            order=Order.objects.filter(order_id=order_id)
            if order.count()<=0:
                response={'detail':'invalid order id','success':'False'}
                return Response(response)
            else:
                order=order.first()
                response={'order_status':order.order_status,'success':'True'}
                return Response(response)



class cancelOrder(CreateAPIView):
    serializer_class = CancelOrderStatusSerializer


    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data,)
        if serializer.is_valid():
            order_id=serializer.validated_data['order_id']
            
            order=Order.objects.filter(order_id=order_id)
            if order.count()<=0:
                response={'detail':'invalid order id','success':'False'}
                return Response(response)
            else:
                order=order.first()
                order.order_status='cancel'
                order.save()
                response={'order_status':order.order_status,'success':'True'}
                return Response(response)



class getUserAddress(CreateAPIView):
    serializer_class = UserAddressSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data,)
        if serializer.is_valid():
            user_phone_number=serializer.validated_data['user_phone_number']
            user=User.objects.filter(phone_number=user_phone_number)[0]
            address=Address.objects.filter(user=user)
            address=address[::-1]
            response=[]
            if len(address)<=3:
                for item in address:
                    response.append(item.address)
            else:
                for item in range(3):
                    response.append(address[item].address)
            return Response({'addresses':response})

class deleteUserAddress(CreateAPIView):
    serializer_class = DeleteUserAddressSerializer

    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data,)
        if serializer.is_valid():
            user_phone_number=serializer.validated_data['user_phone_number']
            address=serializer.validated_data['address']
            userr=User.objects.filter(phone_number=user_phone_number)[0]
            newadd= address[::-1]
            add=newadd.replace(" ","\n",3)
            new=add[::-1]
            address=Address.objects.filter(user=userr,address=new)
            if address.count()<=0:
                return Response({'detail':'invalid address','status':'failed'})
            else:
                address.delete()
                return Response({'status':'success'})



class AddUserAddress(CreateAPIView):
    serializer_class=AddUserAddressSerializer
    def post(self,request,format=None):
        serializer=self.serializer_class(data=request.data,)
        if serializer.is_valid():
            shipping_address = serializer.validated_data['shipping_address']
            state = serializer.validated_data['state']
            country = serializer.validated_data['country']
            zip_code = serializer.validated_data['zip_code']
            user_phone_number=serializer.validated_data['user_phone_number']
            user=User.objects.filter(phone_number=user_phone_number)[0]
            newadd=shipping_address+'\n'+state+'\n'+country+'\n'+zip_code
            obj=Address.objects.filter(user=user,address=newadd)
            if obj.count()<=0:
                address=Address(user=user,address=newadd)
                address.save()
                return Response({'status':'address saved','success':"True"})
            else:
                return Response({'status':'address already exists','success':'False'})
           
        else:
            return Response({'status':'Invalid Format','success':'False'})








class OrdersHistory(CreateAPIView):
    serializer_class = OrderHistorySerializer
    def post(self, request, format=None):
        serializer = self.serializer_class(
            data=request.data,
        )
        if serializer.is_valid():
                user_phone_number = serializer.validated_data['phone_number']
                user=User.objects.filter(phone_number=user_phone_number)[0]
                orders=Order.objects.filter(user=user)
                print(orders)
                orderdetails={}
                i=0

                for order in orders:
                    item_jsons1=order.item_jsons
                    item_jsons1 = order.item_jsons.replace("\'", "\"")

                    item_jsons=json.loads(item_jsons1)
                    j=0
                    productlist={}


                    for product in item_jsons:
                        print("inside loop")

                        productlist[j]={'productId':product,'product_name':item_jsons[product][1],
                                                'quantity':item_jsons[product][0],
                                                'price':item_jsons[product][2],
                                                'add_on1':item_jsons[product][3],
                                                'add_on2':item_jsons[product][4],
                                                'add_on3':item_jsons[product][5],
                                                'add_on4':item_jsons[product][6],
                                                'add_on5':item_jsons[product][7],}
                        j=j+1
                    url='http://127.0.0.1:8000/media/'+str(order.restaurant.photo)
                    orderdetails[i]={'Restaurant':order.restaurant.name,'OrderId':order.order_id,'ProductList':productlist,
                                    'PhoneNumber':order.phone_number,'Name':order.name,'ShippingAddress':order.shipping_address,
                                    'BillingAddress':order.billing_address,'State':order.state,'ZipCode':order.zip_code,
                                    'OrderDate':order.order_date,'OrderTime':order.order_time,'TotalPrice':order.total_price,
                                    'PaymentMode':order.payment_mode,'photo_url':url,'live_video':order.restaurant.live_video}
                    i=i+1
                print(orderdetails)
                return Response({'orderdetails':orderdetails,'success':"true"})





restaurant=''
item_jsons=''
how=''
session_id=''
class Chatboturl(CreateAPIView):



    serializer_class=ChatbotUrlSerializer
    def get(self,request,format=None):


        global restaurant,item_jsons,how,session_id
        restaurant=request.query_params['restaurant_name']
        item_jsons=request.query_params['item_jsons']
        how = request.query_params['how']
        session_id = request.query_params['session_id']
        url='http://127.0.0.1:8000/index/chatbotCheckout/'
        return Response({'url':url})



    def getcontextdict(self):


        global restaurant,item_jsons,how,session_id
        response={'restaurant':restaurant,'item_jsons':item_jsons,'method':how,'session_id':session_id}
        return response





class BookTableAPI(CreateAPIView):
    serializer_class=BookTableSerializer
    def get(self,request,format=None):
        print('inside book a table')
        restaurant_name=request.query_params['restaurant']
        restaurant=Restaurant.objects.filter(name=restaurant_name)[0]
        user_name=request.query_params['user_name']
        user_email=request.query_params['user_email']
        user_phone_number=request.query_params['user_phone_number']
        date=request.query_params['date']
        time=request.query_params['time']
        number_of_people=request.query_params['number_of_people']
        message=request.query_params['message']

        book_table=BookTable(restaurant=restaurant,user_name=user_name,user_phone_number=user_phone_number,
            user_email=user_email,date=date,time=time,number_of_people=number_of_people,message=message)
        book_table.save()

        subject="Eatler India Booking"
        message='Thank you for contacting us,Your booking request has been confirmed for '+number_of_people+' peoples on '+date+' at time : '+time
        send_mail(subject, 
        message, EMAIL_HOST_USER, [user_email], fail_silently = False)
        return Response({'success':'True'})



    
class FeedbackAPI(CreateAPIView):
    serializer_class=FeedbackSerializer
    def get(self,request,format=None):
        message=request.query_params['message']
        category=request.query_params['category']
        fb_type=request.query_params['fb_type']

        feedback=Feedback(message=message,feedback_category=category,feedback_type=fb_type)
        feedback.save()

        return Response({'success':'True'})


class getRestaurantFromCity(CreateAPIView):
    serializer_class=RestaurantFromCitySerializer
    def get(self,request,format=None):
        city=request.query_params['city']
        restaurant=Restaurant.objects.filter(city=city)
        i=0
        response={}
        for object in restaurant:
            url='http://127.0.0.1:8000/media/'+str(object.photo)
            response[i]={'name':object.name,'city':object.city,'address':object.address,
                        'short_description':object.short_description,'long_description':object.long_description,
                        'email':object.email,'contact_number':object.contact_number,'open_time':object.open_time,
                        'close_time':object.close_time,'photo_url':url,'northindian':object.northindian,
                        'southindian':object.southindian,'chinese':object.chinese,'continental':object.continental,
                        'oriental':object.oriental,'veg':object.veg,'non_veg':object.non_veg,'live_video':object.live_video}
            i=i+1
        return Response(response)