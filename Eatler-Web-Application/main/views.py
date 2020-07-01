from django.shortcuts import render,redirect,HttpResponse
from django.urls import reverse_lazy
from django.views.generic import (View,TemplateView,ListView,DetailView,
                                    CreateView,UpdateView,DeleteView)
from .models import Product,Restaurant,Order,Address,UserInfo,Issues,BookTable,Feedback
from accounts.models import User
from .forms import ProductForm,RestaurantForm,RestaurantFormUpdate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from accounts.decorators import allowed_users
from geopy.geocoders import Nominatim
import json
import requests

from django.core import serializers
from datetime import date,datetime,timedelta
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .paytm import Checksum
MERCHANT_KEY = '!mEIW7_rQ@awJKtL'

import os
import dialogflow_v2beta1 as dialogflow
from google.api_core.exceptions import InvalidArgument
import uuid
import cgi
import random
from django.http import JsonResponse
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate
from main.api.views import Chatboturl
from Eatler.settings import EMAIL_HOST_USER,twilio_account_sid,twilio_authtoken
from django.core.mail import send_mail
from accounts.authy_api import send_verfication_code,verify_sent_code
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group


def homepage(request):
    restaurant=Restaurant.objects.all()
    city_list=[]
    locality_dict={}
    for object in restaurant:
        city_list.append(object.city)
        if object.city in locality_dict:
            locality_dict[object.city].append(object.locality)
        else:
            locality_dict[object.city]=[object.locality,]
    for item in locality_dict:
        locality_dict[item]=list(set(locality_dict[item]))

    city_list=set(city_list)
    city_wise_restaurant={}
    for city in city_list:
        this_restaurant=Restaurant.objects.filter(city=city)
        restaurant_list=[]
        for r in this_restaurant:
            restaurant_list.append(r.name)

        city_wise_restaurant[city]=restaurant_list

    print(city_wise_restaurant)
    locality=json.dumps(locality_dict)
    city_wise_restaurant=json.dumps(city_wise_restaurant)
    print(locality)
    context={'city_list':city_list,'locality_list':locality,'city_wise_restaurant':city_wise_restaurant}
    return render(request,'main/index.html',context=context)


def BookTableView(request):
    if request.method=='POST':
        restaurant_name=request.POST.get('city_wise_restaurant')
        restaurant=Restaurant.objects.filter(name=restaurant_name)[0]    
        username=request.POST.get('book_name')
        user_phone_number=request.POST.get('book_phone')
        user_email=request.POST.get('book_email')
        time=request.POST.get('book_time')
        date=request.POST.get('book_date')
        people=request.POST.get('book_people')
        message=request.POST.get('book_message')

        table=BookTable.objects.create(restaurant=restaurant,user_name=username,user_phone_number=user_phone_number,
            user_email=user_email,date=date,time=time,message=message)

        subject="Eatler India Booking"
        message='Thank you for contacting us,Your booking request has been confirmed for '+people+' peoples on '+date+' at time : '+time+' .'
        send_mail(subject, 
        message, EMAIL_HOST_USER, [user_email], fail_silently = False)
        # number="+91" + str(user_phone_number)
        # print(number)
        # client = Client(twilio_account_sid, twilio_authtoken)
        
        # message_number = client.messages.create(
        #     body=message,
        #     to="+918447041758",
        #     from_="+12673103592",
        #     )
           
        # print (message_number.sid)


        return redirect('/')

def getFeedback(request):
    if request.method=='POST':
        print('inside post')
        fb_category=request.POST.get('feedback_category')
        fb=request.POST.get('feedback_message')
        fb_type=""
        payload={'feedback':fb}
        url="https://5aedadaf8223.ngrok.io/predict"
        response = requests.post(url, data=json.dumps(payload),headers={'Content-Type': 'application/json'})
        response_data=response.json()
        try:
            print(response)
            fb_type=response_data['prediction']
            if response.status_code != 200:
                pass
        except:
            pass
        
        feedback=Feedback(message=fb,feedback_category=fb_category,feedback_type=fb_type)
        feedback.save()    
        return redirect('/')



@method_decorator(login_required(login_url="/login/"), name='dispatch')
@method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
class RestaurantListView(ListView):
    context_object_name="restaurants"
    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)

@method_decorator(login_required(login_url="/login/"), name='dispatch')
@method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
class RestaurantCreateView(CreateView):
    # fields=('name','short_description','photo','address','locality','city','email','contact_number')
    form_class=RestaurantForm
    model=Restaurant
    def form_valid(self, form):

        form.instance.user = self.request.user
        
        if 'photo' in self.request.FILES:
            form.instance.photo=self.request.FILES['photo']

        # print(self.request.POST['locality'])
        print(form.cleaned_data['locality'])
        address = str(form.cleaned_data['locality'])+" "+str(form.cleaned_data['city'])
        geolocator = Nominatim(user_agent="main")
        location = geolocator.geocode(address)
        form.instance.latitude=location.latitude
        form.instance.longitude=location.longitude
        return super(RestaurantCreateView, self).form_valid(form)
    success_url=reverse_lazy("main:list_restaurant")


@method_decorator(login_required(login_url="/login/"), name='dispatch')
@method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
class RestaurantDetailView(DetailView):
    context_object_name="restaurant_details"
    model = Restaurant


@method_decorator(login_required(login_url="/login/"), name='dispatch')
@method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
class RestaurantUpdateView(UpdateView):
    form_class=RestaurantFormUpdate
    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)

    def get_success_url(self):
          return reverse_lazy('main:detail_restaurant', kwargs={'pk': self.kwargs['pk']})



@method_decorator(login_required(login_url="/login/"), name='dispatch')
@method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
class RestaurantDeleteView(DeleteView):
    def get_queryset(self):
        return Restaurant.objects.filter(user=self.request.user)
    success_url=reverse_lazy("main:list_restaurant")




#
# @method_decorator(login_required(login_url="/login/"), name='dispatch')
# @method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
# class RestaurantListView(ListView):
#     context_object_name="restaurants"
#     def get_queryset(self):
#         return Restaurant.objects.filter(user=self.request.user)

@method_decorator(login_required(login_url="/login/"), name='dispatch')
@method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
class ProductCreateView(CreateView):
    # fields=('name','description','photo','add_ons','price')
    model=Product
    form_class=ProductForm
    def form_valid(self, form):
        product = form.save(commit=False)
        photo = form.cleaned_data['photo']
        restaurantID=self.kwargs['pk']
        restaurant=Restaurant.objects.get(pk=restaurantID)
        form.instance.restaurant = restaurant
        form.instance.photo=photo
        product.save()
        return super(ProductCreateView, self).form_valid(form)
    def get_success_url(self):
          return reverse_lazy('main:detail_restaurant', kwargs={'pk': self.kwargs['pk']})





@method_decorator(login_required(login_url="/login/"), name='dispatch')
@method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
class ProductUpdateView(UpdateView):
    # fields=('name','short_description','long_description','photo','price','add_on1','add_on2','add_on3','add_on4','add_on5','type','cuisine','time_type')
    form_class=ProductForm
    restaurantID = None
    def get_queryset(self):
        global restaurantID
        productID=self.kwargs['pk']
        product=Product.objects.get(pk=productID)
        restaurant=product.restaurant
        restaurantID=restaurant.pk
        return Product.objects.filter(restaurant=restaurant)


    def get_success_url(self):
          return reverse_lazy('main:detail_restaurant',kwargs={'pk': restaurantID})



@method_decorator(login_required(login_url="/login/"), name='dispatch')
@method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
class ProductDeleteView(DeleteView):
    restaurantID = None
    def get_queryset(self):
        global restaurantID
        productID=self.kwargs['pk']
        product=Product.objects.get(pk=productID)
        restaurant=product.restaurant
        restaurantID=restaurant.pk
        return Product.objects.filter(restaurant=restaurant)


    def get_success_url(self):
          return reverse_lazy('main:detail_restaurant',kwargs={'pk': restaurantID})


@login_required
@allowed_users(allowed_roles=['customer'])
def MenuView(request):
    if request.method=='POST':
        value=request.POST.get('delivery-takeaway')
        locality=""
        if value=="0":
            locality=request.POST.get('locality')
        city=request.POST.get('city')

        restaurant=Restaurant.objects.filter(city=city)
        #takeaway
        if value=="1":
            method='takeaway'
            context={"restaurant":restaurant,'method':method}
            return render(request,'main/takeaway.html',context=context)

        #delivery
        else:
            address=locality+" "+city
            url='http://127.0.0.1:8000/main_api/nearbyRestaurant_get?address=' + address + '&city='+ city
            response=requests.get(url)
            restaurant_obj=response.json()
            if restaurant_obj['status']=='success':
                del restaurant_obj['status']
                restaurant1=restaurant_obj['0']
                url_product='http://127.0.0.1:8000/main_api/product_get?restaurant='+ restaurant1['name']
                response_products=requests.get(url_product)
                products=response_products.json()
                dump_products=json.dumps(products)
                method='delivery'
                context={"restaurants":restaurant_obj,"products":products,"restaurant1":restaurant1,"dump_products":dump_products,'method':method}
                return render(request,'main/delivery.html',context=context)
            else:
                return HttpResponse("vagvhbjn")
    else:
        return render(request,'main/takeaway.html')

@login_required
@allowed_users(allowed_roles=['customer'])
def DeliveryMenuView(request):
    if request.method=='POST':
        name=request.POST.get('restaurant')
        restaurant=Restaurant.objects.filter(name=name).first()
        address=restaurant.locality+" "+restaurant.city
        url='http://127.0.0.1:8000/main_api/nearbyRestaurant_get?address=' + address + '&city='+ restaurant.city
        response=requests.get(url)
        restaurant_obj=response.json()            #all restaurant object
        if restaurant_obj['status']=='success':
            del restaurant_obj['status']
            # restaurant1=restaurant_obj['r']
            url_product='http://127.0.0.1:8000/main_api/product_get?restaurant='+ restaurant.name
            response_products=requests.get(url_product)
            products=response_products.json()
            dump_products=json.dumps(products)
            context={"restaurants":restaurant_obj,"products":products,"restaurant1":restaurant,"dump_products":dump_products}
            return render(request,'main/delivery.html',context=context)



@login_required
@allowed_users(allowed_roles=['customer'])
def RestaurantMenuView(request,pk):
    restaurant=Restaurant.objects.filter(pk=pk).first()
    restaurant_obj=Restaurant.objects.filter(pk=pk)[0]
    url_product='http://127.0.0.1:8000/main_api/product_get?restaurant='+ restaurant.name
    response_products=requests.get(url_product)
    products=response_products.json()
    dump_products=json.dumps(products)

    context={"products":products,"restaurant1":restaurant_obj,"dump_products":dump_products}
    return render(request,"main/menu.html",context=context)


@login_required
@allowed_users(allowed_roles=['customer'])
def CheckoutView(request):
    if request.method=="POST":
        user = request.user
        item_jsons1=request.POST.get('item_jsons',)
        item_jsons=json.loads(item_jsons1)
        product_key=next(iter(item_jsons))
        product=Product.objects.filter(pk=product_key).first()
        restaurant=Restaurant.objects.filter(name=product.restaurant)[0]
        name = request.POST.get('name',)
        phone_number=request.POST.get('phone_number',)
        email = request.POST.get('email')

        if request.POST.get('inlineRadioOptions')!='other':
            shipping_address = request.POST.get('inlineRadioOptions')
            print(type(shipping_address))
            print(shipping_address)
        else:
            if request.POST.get('address2',)!="":
                shipping_address = request.POST.get('address',) + ' ' + request.POST.get('address2',)
                print("Indside ehehehehehe")
                print(type(shipping_address))
                print(shipping_address)
            else:
                shipping_address = request.POST.get('address',) 
                print("Indside ehehehehehe")
                print(type(shipping_address))
                print(shipping_address)
        billing_address = request.POST.get('address_billing',) + ' ' + request.POST.get('address2_billing',)+ ' ' +request.POST.get('state_billing',)+' '+request.POST.get('country_billing')+' '+request.POST.get('zip_billing')
        state = request.POST.get('state',)
        country = request.POST.get('country',)
        zip_code = request.POST.get('zip',)
        total_price= request.POST.get('total_price',)
        special_instruction=request.POST.get('special_instruction')
        how=request.POST.get('method')
        schedule_date=request.POST.get('date')
        schedule_time=request.POST.get('time')

        order=Order(user=user,restaurant=restaurant,item_jsons=item_jsons,name=name,phone_number=phone_number,email=email,
                    shipping_address=shipping_address,billing_address=billing_address,state=state,country=country,zip_code=zip_code,total_price=total_price,
                    special_instruction=special_instruction,schedule_date=schedule_date,schedule_time=schedule_time,how=how)

        # product_list={}

        # for product in item_jsons:
        #     product_list[product]={'product_name':item_jsons[product][1],
        #                             'quantity':item_jsons[product][0],
        #                             'price':item_jsons[product][2],
        #                             'add_on1':item_jsons[product][3],
        #                             'add_on2':item_jsons[product][4],
        #                             'add_on3':item_jsons[product][5],
        #                             'add_on4':item_jsons[product][6],
        #                             'add_on5':item_jsons[product][7],}



        # item_jsons = currentorder.item_jsons.replace("\'", "\"")
        # item_jsons = json.loads(item_jsons)
        temp_product_list={}
        product_list={}
        for product in item_jsons:
            temp_product_list[product]={'product_name':item_jsons[product][1],
                                    'quantity':item_jsons[product][0],
                                    'price':item_jsons[product][2],
                                    'add_on1':item_jsons[product][3],
                                    'add_on2':item_jsons[product][4],
                                    'add_on3':item_jsons[product][5],
                                    'add_on4':item_jsons[product][6],
                                    'add_on5':item_jsons[product][7],}
        product_list[order.order_id]=temp_product_list

        decider=request.POST.get('payment_method')
        if decider=='COD':
            order.order_status='pending'
            order.payment_mode='COD'
            order.payment_status=False
        
            if request.POST.get('inlineRadioOptions')=='other':
                newadd=shipping_address+'\n'+state+'\n'+country+'\n'+zip_code
                obj=Address.objects.filter(user=user,address=newadd)
                if obj.count()<=0:
                    address=Address(user=user,address=newadd)
                    address.save()

                
            order.save()
            id=order.order_id
            response={'ORDERID':id,'TXNAMOUNT':total_price,'PAYMENTMODE':'COD','RESPCODE':'01',
                'product_list':product_list,'id':id,'name':order.name,'restaurant':order.restaurant.name,'time':order.order_time,'date':order.order_date,
                'order_status':order.order_status,'link':order.restaurant.live_video,'total':order.total_price,
                'payment_mode':'COD','paymentstatus':order.payment_status}
            return render(request,'main/orderstatus.html',context={'response':response})

        else:
            order.save()
            if request.POST.get('inlineRadioOptions')=='other':
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
                'CUST_ID':str(user.phone_number),
                'INDUSTRY_TYPE_ID':'Retail',
                'WEBSITE':'WEBSTAGING',
                'CHANNEL_ID':'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/index/handleRequest/',
            }
            data_dict['CHECKSUMHASH']=Checksum.generate_checksum(data_dict,MERCHANT_KEY)
            return render(request,'main/paytm.html',{'param_dict':data_dict})
    else:
        user = request.user
        address = Address.objects.filter(user=user)
        response={}
        # response=model_to_dict(address)
        i=0
        for item in address:
                response[i]=item.address
                i=i+1
        print(response)
        return render(request,'main/checkout.html',{'address':response})

@login_required
@allowed_users(allowed_roles=['customer'])
def CheckoutTakeawayView(request):
    if request.method=="POST":
        user = request.user
        item_jsons1=request.POST.get('item_jsons',)
        item_jsons=json.loads(item_jsons1)
        product_key=next(iter(item_jsons))
        product=Product.objects.filter(pk=product_key).first()
        restaurant=Restaurant.objects.filter(name=product.restaurant)[0]
        name = request.POST.get('name',)
        phone_number=request.POST.get('phone_number',)
        email = request.POST.get('email')
        total_price= request.POST.get('total_price',)
        special_instruction=request.POST.get('special_instruction')
        how=request.POST.get('method')
        schedule_date=request.POST.get('date')
        schedule_time=request.POST.get('time')

        order=Order(user=user,restaurant=restaurant,item_jsons=item_jsons,name=name,phone_number=phone_number,email=email,total_price=total_price,
                    special_instruction=special_instruction,schedule_date=schedule_date,schedule_time=schedule_time,how=how)

        product_list={}

        # for product in item_jsons:
        #     product_list[product]={'product_name':item_jsons[product][1],
        #                             'quantity':item_jsons[product][0],
        #                             'price':item_jsons[product][2],
        #                             'add_on1':item_jsons[product][3],
        #                             'add_on2':item_jsons[product][4],
        #                             'add_on3':item_jsons[product][5],
        #                             'add_on4':item_jsons[product][6],
        #                             'add_on5':item_jsons[product][7],}


        temp_product_list={}
        product_list={}
        for product in item_jsons:
            temp_product_list[product]={'product_name':item_jsons[product][1],
                                    'quantity':item_jsons[product][0],
                                    'price':item_jsons[product][2],
                                    'add_on1':item_jsons[product][3],
                                    'add_on2':item_jsons[product][4],
                                    'add_on3':item_jsons[product][5],
                                    'add_on4':item_jsons[product][6],
                                    'add_on5':item_jsons[product][7],}
        product_list[order.order_id]=temp_product_list

        decider=request.POST.get('payment_method')
        if decider=='COD':
            order.order_status='pending'
            order.payment_mode='COD'
            order.payment_status=False    
            order.save()
            id=order.order_id
            response={'ORDERID':id,'TXNAMOUNT':total_price,'PAYMENTMODE':'COD','RESPCODE':'01',
                'product_list':product_list,'id':id,'name':order.name,'restaurant':order.restaurant.name,'time':order.order_time,'date':order.order_date,
                'order_status':order.order_status,'link':order.restaurant.live_video,'total':order.total_price,
                'payment_mode':"COD",'paymentstatus':order.payment_status
                }
            return render(request,'main/orderstatus.html',context={'response':response})

        else:
            order.save()
            id=order.order_id
           
            data_dict = {
                'MID':'aVrRqW70498541104158',
                'ORDER_ID':str(order.order_id),
                'TXN_AMOUNT':str(order.total_price),
                'CUST_ID':str(user.phone_number),
                'INDUSTRY_TYPE_ID':'Retail',
                'WEBSITE':'WEBSTAGING',
                'CHANNEL_ID':'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/index/handleRequest/',

            }
            data_dict['CHECKSUMHASH']=Checksum.generate_checksum(data_dict,MERCHANT_KEY)
            print(data_dict)
            return render(request,'main/paytm.html',{'param_dict':data_dict})
    



    else:
        return render(request,'main/checkout_takeaway.html')





# delivery point of view
def chatbotCheckout(request):
    if request.method=='GET':
        print('hi')
        chatbot=Chatboturl()
        apnacontext=chatbot.getcontextdict()
        session_id=apnacontext['session_id']
        method=apnacontext['method']              #only delivery or takeaway
        restaurant_name=apnacontext['restaurant']
        item_jsons=apnacontext['item_jsons']
        item_jsons =item_jsons.replace("\'", "\"")
        item_jsons = json.loads(item_jsons)
        item_jsons=json.dumps(item_jsons)

        response={'restaurant':restaurant_name,'item_jsons':item_jsons,'method':method,'session_id':session_id}
        if method=='delivery':
            return render(request,'main/chatbotCheckout.html',{'response':response})
        else:
            return render(request,'main/chatbotCheckout_takeaway.html',{'response':response})




    elif request.method=="POST":
        if request.POST.get('method')=='delivery' or request.POST.get('method')=='schedule-delivery':
            name=request.POST.get('name',)
            user_phone_number=request.POST.get('user_phone_number',)
            country_code=91
            user=User.objects.filter(phone_number=user_phone_number)
            if len(user)<=0:
                user=User(full_name=name,phone_number=user_phone_number,country_code=91)
                user.save()
                token, _ = Token.objects.get_or_create(user=user)
                group = Group.objects.get(name='customer')
                user.groups.add(group)
            else:
                user=user.first()
            session_id=request.POST.get('session_id')
            item_jsons1=request.POST.get('item_jsons',)
            item_jsons=json.loads(item_jsons1)
            restaurant_name=request.POST.get('restaurant')
            restaurant=Restaurant.objects.filter(name=restaurant_name)[0]
            phone_number=request.POST.get('phone_number',)
            email = request.POST.get('email')
            shipping_address=''
            if request.POST.get('address2',)!="":
                shipping_address = request.POST.get('address',) + ' ' + request.POST.get('address2',)
            else:
                shipping_address = request.POST.get('address',)
            billing_address = request.POST.get('address_billing',) + ' ' + request.POST.get('address2_billing',)+ ' ' +request.POST.get('state_billing',)+' '+request.POST.get('country_billing')+' '+request.POST.get('zip_billing')
            state = request.POST.get('state',)
            country = request.POST.get('country',)
            zip_code = request.POST.get('zip',)
            total_price= request.POST.get('total_price',)

            special_instruction=request.POST.get('special_instruction')
            how=request.POST.get('method')
            schedule_date=request.POST.get('date')
            schedule_time=request.POST.get('time')

            order=Order(user=user,restaurant=restaurant,item_jsons=item_jsons,name=name,phone_number=phone_number,email=email,
                    shipping_address=shipping_address,billing_address=billing_address,state=state,country=country,zip_code=zip_code,total_price=total_price,
                    special_instruction=special_instruction,schedule_date=schedule_date,schedule_time=schedule_time,how=how,session_id=session_id)
            product_list={}

            for product in item_jsons:
                product_list[product]={'product_name':item_jsons[product][1],
                                        'quantity':item_jsons[product][0],
                                        'price':item_jsons[product][2],
                                        'add_on1':item_jsons[product][3],
                                        'add_on2':item_jsons[product][4],
                                        'add_on3':item_jsons[product][5],
                                        'add_on4':item_jsons[product][6],
                                        'add_on5':item_jsons[product][7],}

            decider=request.POST.get('payment_method')
            if decider=='COD':
                order.order_status='pending'
                order.payment_mode='COD'
                order.payment_status=False
                try:
                    newadd=shipping_address+'\n'+state+'\n'+country+'\n'+zip_code
                    obj=Address.objects.filter(user=user,address=newadd)
                    if obj.count()<=0:
                        address=Address(user=user,address=newadd)
                        address.save()
                except:
                    raise

                order.save()
                id=order.order_id
                if session_id!=None:
                    payload={'order_id':order.order_id,'order_status':order.order_status,'order_payment_status':order.payment_status,'total_price':order.total_price,'customer_name':order.name,'session_id':session_id}
                    url="https://e81a67d4b3fe.ngrok.io/order_status"
                    respponse = requests.post(url, data=json.dumps(payload),headers={'Content-Type': 'application/json'})
                    print(respponse)
                    print(respponse.status_code)

                    if respponse.status_code != 200:

                        raise ValueError('Request to slack returned an error %s, the response is:\n%s'% (respponse.status_code, respponse.text))



                response={'ORDERID':id,'TXNAMOUNT':total_price,'PAYMENTMODE':'COD','RESPCODE':'01',
                'product_list':product_list,'id':id,'name':order.name,'restaurant':order.restaurant.name,'time':order.order_time,'date':order.order_date,
                'order_status':order.order_status,'link':order.restaurant.live_video,'total':order.total_price,
                'payment_mode':"COD",'paymentstatus':order.payment_status
                }
                return render(request,'main/orderstatus.html',context={'response':response})

            else:           
                order.save()
                try:
                    newadd=shipping_address+'\n'+state+'\n'+country+'\n'+zip_code
                    obj=Address.objects.filter(user=user,address=newadd)
                    if obj.count()<=0:
                        address=Address(user=user,address=newadd)
                        address.save()

                except Exception as e:
                    raise
                    

                id=order.order_id
                data_dict = {
                    'MID':'aVrRqW70498541104158',
                    'ORDER_ID':str(order.order_id),
                    'TXN_AMOUNT':str(order.total_price),
                    'CUST_ID':str(user.phone_number),
                    'INDUSTRY_TYPE_ID':'Retail',
                    'WEBSITE':'WEBSTAGING',
                    'CHANNEL_ID':'WEB',
                    'CALLBACK_URL':'http://127.0.0.1:8000/index/handleRequest/',
                }
                data_dict['CHECKSUMHASH']=Checksum.generate_checksum(data_dict,MERCHANT_KEY)
                return render(request,'main/paytm.html',{'param_dict':data_dict})

        else:          #takeaway
            name=request.POST.get('name',)
            user_phone_number=request.POST.get('user_phone_number',)
            country_code=91
            user=User.objects.filter(phone_number=user_phone_number)
            if len(user)<=0:
                user=User.objects.create(full_name=name,phone_number=user_phone_number,country_code=91)
                user.save()
                token, _ = Token.objects.get_or_create(user=user)
                group = Group.objects.get(name='customer')
                user.groups.add(group)
            else:
                user=user.first()

            session_id=request.POST.get('session_id')
            item_jsons1=request.POST.get('item_jsons',)
            item_jsons=json.loads(item_jsons1)
            restaurant_name=request.POST.get('restaurant')
            restaurant=Restaurant.objects.filter(name=restaurant_name)[0]
            email=request.POST.get('email',)
            phone_number=request.POST.get('phone_number',)
            total_price= request.POST.get('total_price',)
            special_instruction=request.POST.get('special_instruction')
            how=request.POST.get('method')
            schedule_date=request.POST.get('date')
            schedule_time=request.POST.get('time')

            order=Order(user=user,restaurant=restaurant,item_jsons=item_jsons,name=name,phone_number=phone_number,email=email,total_price=total_price,
                        special_instruction=special_instruction,schedule_date=schedule_date,schedule_time=schedule_time,how=how,session_id=session_id)

            product_list={}

            for product in item_jsons:
                product_list[product]={'product_name':item_jsons[product][1],
                                        'quantity':item_jsons[product][0],
                                        'price':item_jsons[product][2],
                                        'add_on1':item_jsons[product][3],
                                        'add_on2':item_jsons[product][4],
                                        'add_on3':item_jsons[product][5],
                                        'add_on4':item_jsons[product][6],
                                        'add_on5':item_jsons[product][7],}

            decider=request.POST.get('payment_method')
            if decider=='COD':
                order.order_status='pending'
                order.payment_mode='COD'
                order.payment_status=False    
                order.save()
                id=order.order_id
                if session_id!=None:
                    payload={'order_id':order.order_id,'order_status':order.order_status,'order_payment_status':order.payment_status,'total_price':order.total_price,'customer_name':order.name,'session_id':session_id}
                    url="https://e81a67d4b3fe.ngrok.io/order_status"
                    respponse = requests.post(url, data=json.dumps(payload),headers={'Content-Type': 'application/json'})
                    print(respponse)
                    print(respponse.status_code)

                    if respponse.status_code != 200:

                        raise ValueError('Request to slack returned an error %s, the response is:\n%s'% (respponse.status_code, respponse.text))



                response={'ORDERID':id,'TXNAMOUNT':total_price,'PAYMENTMODE':'COD','RESPCODE':'01',
                'product_list':product_list,'id':id,'name':order.name,'restaurant':order.restaurant.name,'time':order.order_time,'date':order.order_date,
                'order_status':order.order_status,'link':order.restaurant.live_video,'total':order.total_price,
                'payment_mode':"COD",'paymentstatus':order.payment_status
                }
                return render(request,'main/orderstatus.html',context={'response':response})

            else:
                order.save()
                id=order.order_id
                data_dict = {
                    'MID':'aVrRqW70498541104158',
                    'ORDER_ID':str(order.order_id),
                    'TXN_AMOUNT':str(order.total_price),
                    'CUST_ID':str(user.phone_number),
                    'INDUSTRY_TYPE_ID':'Retail',
                    'WEBSITE':'WEBSTAGING',
                    'CHANNEL_ID':'WEB',
                    'CALLBACK_URL':'http://127.0.0.1:8000/index/handleRequest/',
                }
                data_dict['CHECKSUMHASH']=Checksum.generate_checksum(data_dict,MERCHANT_KEY)
                return render(request,'main/paytm.html',{'param_dict':data_dict})
    





@csrf_exempt
def handleRequest(request):
    form = request.POST
    response_dict={}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
        if i== 'ORDERID':
            id=form['ORDERID']
        if i== "PAYMENTMODE":
            payment_mode=form[i]

    order=Order.objects.filter(order_id=id)[0]
    user=order.user
    verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
    session_id=order.session_id
    item_jsons = order.item_jsons.replace("\'", "\"")
    item_jsons = json.loads(item_jsons)
    temp_product_list={}
    product_list={}
    for product in item_jsons:
        temp_product_list[product]={'product_name':item_jsons[product][1],
                                'quantity':item_jsons[product][0],
                                'price':item_jsons[product][2],
                                'add_on1':item_jsons[product][3],
                                'add_on2':item_jsons[product][4],
                                'add_on3':item_jsons[product][5],
                                'add_on4':item_jsons[product][6],
                                'add_on5':item_jsons[product][7],}
    product_list[order.order_id]=temp_product_list
    print(product_list)



    if verify:
        if response_dict['RESPCODE'] == '01':
            order.payment_status=True
            order.payment_mode=payment_mode
            order.order_status="pending"
            order.save()
        else:
            Order.objects.filter(order_id=id).delete()
            print('order was not successful because' + response_dict['RESPMSG'])

    if session_id!=None:
        payload={'order_id':order.order_id,'order_status':order.order_status,'order_payment_status':order.payment_status,'total_price':order.total_price,'customer_name':order.name,'session_id':session_id}
        url="https://e81a67d4b3fe.ngrok.io/order_status"
        respponse = requests.post(url, data=json.dumps(payload),headers={'Content-Type': 'application/json'})
        print(respponse)
        print(respponse.status_code)

        if respponse.status_code != 200:
            raise ValueError('Request to slack returned an error %s, the response is:\n%s'% (respponse.status_code, respponse.text))


    response_dict['name']=order.name
    response_dict['restaurant']=order.restaurant.name
    response_dict['date']=order.order_date
    response_dict['time']=order.order_time
    response_dict['product_list']=product_list
    response_dict['order_status']=order.order_status
    response_dict['link']=order.restaurant.live_video
    response_dict['total']=order.total_price
    response_dict['id']=id
    response_dict['paymentstatus']=order.payment_status
    response_dict['payment_mode']=order.payment_mode
    response_dict['how']=order.how
    print(response_dict['product_list'])
    return render(request, 'main/orderstatus.html', {'response': response_dict,'user':user})










def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def integration(request):
    if request.method == 'POST' and request.is_ajax():
        text_to_be_analyzed = request.POST.get('message', None)
        print(text_to_be_analyzed)
        print(type(text_to_be_analyzed))
        user_name = ""
        if request.user.is_authenticated:
            user_name = request.user.full_name
        sessionid = get_client_ip(request)
        response_data = detect_intent(text_to_be_analyzed, user_name, sessionid)
        return JsonResponse(response_data)


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
    status = 1
    url = None
    Buttons = []
    if intent == 'Welcome Intent' or intent == 'chatbot_active':
        if user != '':
            text = random.choice([
                'Hi ' + user + '! I see you have great taste coming to the world\'s first transparent kitchen. I am Vafer, your virtual waiter. How would you like my assistance today?',
                'Hey ' + user + '! How are you doing today? I am Vafer, your virtual waiter and aid. How may I help you today?',
                'Hey there ' + user + '! Great choice entering the world\'s first transparent eatery. I am Vafer, your virtual waiter. Any way I can help you today?',
                'Hello ' + user + '! Welcome to the world\'s first transparent eatery. I am Vafer, your virtual waiter. How may I assist you today?'])
        Buttons = ['Log in/Sign up', 'Let\'s Talk 💬']
    elif intent == 'Order':
        text='Please click the "Order now" button on the website home page'
    elif intent=='Book':
        text = 'Please click the "Book a table" button on the website home page'
    elif intent=='Login':
        if user=='':
            url='/login_verify'
            status=0
        else:
            text='You are already logged in.'
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
        url='127.0.0.1:5000/predict'
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
             'status': status,  # status=0 ,url=login url , status = 1 url= none
             'url': url
             }

    response_data = {'reply': reply, 'intent': intent}
    return response_data




@csrf_exempt
def updateStatus(request):
    if request.method=='POST' and request.is_ajax():
        status=request.POST.get('status',None)
        order_id=request.POST.get('id',None)
        order=Order.objects.filter(order_id=order_id)[0]
        order.order_status=status
        order.save()
        response_dict={'order_id':order.order_id,'order_status':order.order_status,'total_price':order.total_price,
                        'order_date':order.order_date,'order_time':order.order_time}
        return JsonResponse(response_dict)
    else:
        return JsonResponse({"status":'fail'})




# def orderStatus(request,order_id):
#     order = order_id
#     try:
#         currentorder= Order.objects.filter(order_id=order)
#         if len(currentorder)<=0:
#             return redirect('/index/checkout/')
#     except:
#         raise
#     # live view link of the restaurant needs to added like this :  currentorder.restaurant.link and return to the response
#     currentorder=Order.objects.filter(order_id=order).first()
#     link = currentorder.restaurant.live_video
#     item_jsons = currentorder.item_jsons.replace("\'", "\"")
#     item_jsons = json.loads(item_jsons)
#     temp_product_list={}
#     product_list={}
#     for product in item_jsons:
#         temp_product_list[product]={'product_name':item_jsons[product][1],
#                                 'quantity':item_jsons[product][0],
#                                 'price':item_jsons[product][2],
#                                 'add_on1':item_jsons[product][3],
#                                 'add_on2':item_jsons[product][4],
#                                 'add_on3':item_jsons[product][5],
#                                 'add_on4':item_jsons[product][6],
#                                 'add_on5':item_jsons[product][7],}
#     product_list[currentorder.order_id]=temp_product_list

#     response_dict={'id':order,'name':currentorder.name,'restaurant':currentorder.restaurant.name,'time':currentorder.order_time,'date':currentorder.order_date,
#     'order_status':currentorder.order_status,'link':link,'total':currentorder.total_price,
#     'payment_mode':currentorder.payment_mode,'paymentstatus':currentorder.payment_status}

#     response_dict['product_list']=product_list
#     return render(request,'main/orderstatus.html',{'response':response_dict})






def sendEmail(request):
    if request.method=='POST':
        recepient=request.POST.get('email',)
        message=request.POST.get('message',)
        fname=request.POST.get('name',)
        lname=request.POST.get('lastname',)
        phone=request.POST.get('phone',)
        category=request.POST.get('category',)

        subject=request.POST.get('subject',)
        issue=Issues(first_name=fname,last_name=lname,email=recepient,subject=subject,phone_number=phone,message=message,category=category)

        if 'file' in request.FILES:
            file=request.FILES['file']
            issue.file=file
        issue.save()
        message=message+'\n\n'+'Thank you for contacting us, will try to resolve your issue as soon as possible'
        subject='Eatler Customer Care'
        send_mail(subject, 
        message, EMAIL_HOST_USER, [recepient], fail_silently = False)
        return redirect('/')

        

@csrf_exempt
def checkNumber(request):
    print('here')
    if request.method=="POST" and request.is_ajax():
        phone_number=request.POST.get('phone_number',None)
        country_code=91

        user={'phone_number':phone_number,'country_code':country_code}
        response = send_verfication_code(user)
        data = json.loads(response.text)

        if data['success'] == False:
            dict = {'status': 'OTP not send! Try Again', 'success': 'False'}
            return JsonResponse(dict)
        else:
            dict = { 'status': 'OTP Sent successfully', 'phone_number': phone_number, 'success': 'True'}
            return JsonResponse(dict)



@csrf_exempt
def verifyOTP(request):
    print("inside verify otp")
    if request.method=="POST" and request.is_ajax():
        otp=request.POST.get('otp',None)
        phone_number=request.POST.get('phone_number',None)
        country_code=91
        user={'phone_number':phone_number,'country_code':country_code}
        response = verify_sent_code(otp, user)
        data = json.loads(response.text)
        if data['success'] == True:
            return JsonResponse({'success':'True'})
        else:
            return JsonResponse({'success':'False'})



@login_required
@allowed_users(allowed_roles=['customer'])
def ProfileView(request):
    if request.method=="POST":
        user=request.user
        full_name=request.POST.get('full_name')
        email=request.POST.get('email')
        userInfo=UserInfo.objects.filter(user=user)
        if len(userInfo)<=0:
            userInfo=UserInfo.objects.create(user=user,email=email)
        else:
            userInfo=userInfo.first()
        user.full_name=full_name
        user.save()
        userInfo.email=email
        if 'photo' in request.FILES:
            userInfo.photo=request.FILES['photo']
        userInfo.save()


        address=Address.objects.filter(user=user)
        address=address[::-1]
        orders=Order.objects.filter(user=user)
        orders=orders[::-1]
        total_orders=len(orders)
        total_address=len(address)

        product_list={}
        for currentorder in orders:
            item_jsons = currentorder.item_jsons.replace("\'", "\"")
            item_jsons = json.loads(item_jsons)
            temp_product_list={}
            for product in item_jsons:
                temp_product_list[product]={'product_name':item_jsons[product][1],
                                        'quantity':item_jsons[product][0],
                                        'price':item_jsons[product][2],
                                        'add_on1':item_jsons[product][3],
                                        'add_on2':item_jsons[product][4],
                                        'add_on3':item_jsons[product][5],
                                        'add_on4':item_jsons[product][6],
                                        'add_on5':item_jsons[product][7],}
            product_list[currentorder.order_id]=temp_product_list
        return render(request,"main/profile.html",{'address':address,'orders':orders,'data':user,'userInfo':userInfo,'product_list':product_list,'total_orders':total_orders,'total_address':total_address})
    
    else:
        user=request.user
        address=Address.objects.filter(user=user)
        address=address[::-1]
        orders=Order.objects.filter(user=user)
        orders=orders[::-1]
        total_orders=len(orders)
        total_address=len(address)
        userInfo=UserInfo.objects.filter(user=user)
        if len(userInfo)<=0:
            userInfo={}
        else:
            userInfo=userInfo.first()
        product_list={}
        for currentorder in orders:
            item_jsons = currentorder.item_jsons.replace("\'", "\"")
            item_jsons = json.loads(item_jsons)
            temp_product_list={}
            for product in item_jsons:
                temp_product_list[product]={'product_name':item_jsons[product][1],
                                        'quantity':item_jsons[product][0],
                                        'price':item_jsons[product][2],
                                        'add_on1':item_jsons[product][3],
                                        'add_on2':item_jsons[product][4],
                                        'add_on3':item_jsons[product][5],
                                        'add_on4':item_jsons[product][6],
                                        'add_on5':item_jsons[product][7],}
            product_list[currentorder.order_id]=temp_product_list
        return render(request,'main/profile.html',{'address':address,'orders':orders,'data':user,'userInfo':userInfo,'product_list':product_list,'total_orders':total_orders,'total_address':total_address})



@csrf_exempt
def DeleteAddress(request):
    print('inside delete')
    if request.method=="POST" and request.is_ajax():
        address_id=request.POST.get('id',)
        address=Address.objects.filter(pk=address_id).delete()
        return JsonResponse({'success':'True'})
    else:
        return JsonResponse({'success':'False'})
        


        