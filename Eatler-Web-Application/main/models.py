from django.db import models
from accounts.models import User
from django.shortcuts import redirect
from django.urls import reverse
import os
# Create your models here.
from django_google_maps import fields as map_fields
from datetime import date,datetime
from django.utils import timezone




class Restaurant(models.Model):

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    short_description = models.CharField(max_length=200)
    long_description = models.TextField()
    photo = models.ImageField(upload_to='restaurant_images',blank=True)
    address = models.CharField(max_length=300)
    locality = models.CharField(max_length=200,default=None)
    city = models.CharField(max_length=200)
    email = models.EmailField()
    contact_number = models.IntegerField()
    latitude=models.FloatField(blank=True,null=True)
    longitude=models.FloatField(blank=True,null=True)
    open_time=models.TimeField(auto_now=False, auto_now_add=False)
    close_time=models.TimeField(auto_now=False, auto_now_add=False)
    rating = models.CharField(max_length=30,blank=True,default=None,null=True)
    northindian=models.BooleanField(default=True)
    southindian=models.BooleanField(default=True)
    chinese=models.BooleanField()
    continental=models.BooleanField()
    oriental=models.BooleanField()
    veg=models.BooleanField(default=True)
    non_veg=models.BooleanField(default=False)
    live_video=models.URLField(max_length=300,default="")

    def __str__(self):
        return self.name


    def get_absolute_url(self):
        return reverse("main:list")



TYPE = (
('VEG','veg'),
('NON_VEG','non_veg'),
)

CUISINE = (
('NorthIndian','northindian'),
('SouthIndian','southindian'),
('Chinese','chinese'),
('Continental','continental'),
('Oriental','oriental'),
)

CATEGORY = (
('Breakfast','breakfast'),
('Snacks','snacks'),
('Lunch/dinner','lunch/dinner'),
('Beverages','beverages'),
('Dessert/sweet','dessert/sweet')
)




class Product(models.Model):
    restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE,related_name="products",default=None)
    name = models.CharField(max_length=300)
    short_description = models.CharField(max_length=200)
    long_description = models.TextField(blank=True)
    photo = models.ImageField(upload_to='product_images',blank=True)
    price = models.DecimalField(max_digits=6,decimal_places=2)
    add_on1 = models.CharField(max_length=200,default=None,blank=True)
    add_on2 = models.CharField(max_length=200,default=None,blank=True)
    add_on3 = models.CharField(max_length=200,default=None,blank=True)
    add_on4 = models.CharField(max_length=200,default=None,blank=True)
    add_on5 = models.CharField(max_length=200,default=None,blank=True)
    type = models.CharField(max_length=20,choices=TYPE,default='Veg')
    cuisine = models.CharField(max_length=20,choices=CUISINE,default='NothIndian')
    category = models.CharField(max_length=30,choices=CATEGORY,default='Lunch/Dinner')
    rating = models.CharField(max_length=30,blank=True,default=None,null=True)

    def __str__(self):
        return self.name



class Order(models.Model):
    order_id=models.AutoField(primary_key=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    phone_number=models.CharField(max_length=111)
    item_jsons=models.CharField(max_length=6000)
    name = models.CharField(max_length=300)
    email = models.EmailField(max_length=200)
    shipping_address = models.CharField(max_length=200,default="")
    billing_address = models.CharField(max_length=200,default="")
    state = models.CharField(max_length=200,default="")
    country = models.CharField(max_length=200,default="")
    order_time=models.TimeField(auto_now_add=True,editable=True)
    order_date=models.DateField(auto_now_add=True,editable=True)
    zip_code = models.CharField(max_length=200,blank=True,null=True,default="")
    total_price=models.CharField(max_length=50,blank=True,null=True)
    order_status=models.CharField(max_length=200,default="not_placed")
    payment_status=models.BooleanField(default=False)
    payment_mode=models.CharField(max_length=200,default="")
    special_instruction=models.CharField(max_length=1000,default="")
    how=models.CharField(max_length=30,default="delivery")
    schedule_date=models.DateField(auto_now_add=False,editable=True,default=None,blank=True)
    schedule_time=models.TimeField(auto_now_add=False,editable=True,default=None,blank=True)
    session_id=models.CharField(max_length=300,default=None,null=True)





class Address(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    address = models.CharField(max_length=200,unique=True)

    def __str__(self):
        return self.address

STATUS=(
    ('Resolved','resolved'),
    ('Unresolved','unresolved')
)

class Issues(models.Model):

    first_name=models.CharField(max_length=20)
    last_name=models.CharField(max_length=20)
    phone_number=models.IntegerField()
    subject=models.CharField(max_length=150)
    message=models.CharField(max_length=1000)
    category=models.CharField(max_length=20)
    file = models.FileField(upload_to='Issues',blank=True)
    status=models.CharField(choices=STATUS,max_length=30,default='Unresolved')
    email=models.EmailField()

    def _str_(self):
        return self.first_name





class UserInfo(models.Model):
    user_info_id=models.AutoField(primary_key=True)
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    email = models.EmailField(default="",blank=True)
    photo = models.ImageField(upload_to='user_image',blank=True)


    def __str__(self):
        return self.user.full_name




class BookTable(models.Model):
    book_id=models.AutoField(primary_key=True)
    restaurant=models.ForeignKey(Restaurant,on_delete=models.CASCADE)
    user_name=models.CharField(max_length=30)
    user_email=models.EmailField()
    user_phone_number=models.IntegerField()
    date=models.DateField(auto_now_add=False,editable=True,default=None,blank=True)
    time=models.TimeField(auto_now_add=False,editable=True,default=None,blank=True)
    number_of_people=models.IntegerField(default=0)
    message=models.CharField(max_length=400,blank=True)



class Feedback(models.Model):
    feedback_id=models.AutoField(primary_key=True)
    message=models.CharField(max_length=2000)
    feedback_type=models.CharField(max_length=30)
    feedback_category=models.CharField(max_length=30)

#cancel reason 
#delivery person
#delivery charge
#deliverable time how much time required to reach the destination




# pending
# confirm
# preparing
# outfordelivery
# cancelled
# delivered






#delivery
#checkout me address ko validate karna and calculate delivery charge accordingly
#cancel ka reason puchna
#modify order model
