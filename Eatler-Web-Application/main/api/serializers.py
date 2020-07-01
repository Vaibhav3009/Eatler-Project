from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from main.models import Product,Restaurant,Order,Address,BookTable,Feedback
from phonenumber_field.formfields import PhoneNumberField


# class ProductSerializer(ModelSerializer):
#     name = serializers.CharField()
#      = serializers.IntegerField()
#
#     class Meta:
#         model = User
#         fields = ('phone_number','country_code')


class RestaurantSerializer(ModelSerializer):
    query = serializers.CharField()
    class Meta:
        model = Restaurant
        fields = ['query']


class ProductSerializer(ModelSerializer):
    restaurant = serializers.CharField()

    class Meta:
        model = Product
        fields = ['restaurant']


class AddressSerializer(ModelSerializer):
    address=serializers.CharField()

    class Meta:
        model = Restaurant
        fields = ['address']



class NearbyRestaurantSerializer(ModelSerializer):
    address=serializers.CharField()
    city=serializers.CharField()

    class Meta:
        model=Restaurant
        fields=['address','city']


class IntegrationSerializer(serializers.Serializer):
    message=serializers.CharField()
    user_name=serializers.CharField()



class OrderSerializer(ModelSerializer):
    user_phone_number = serializers.IntegerField()
    restaurant=serializers.CharField()
    phone_number=serializers.CharField()
    item_jsons=serializers.CharField()
    name = serializers.CharField()
    email = serializers.EmailField()
    shipping_address = serializers.CharField()
    billing_address = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()
    zip_code = serializers.CharField()
    total_price=serializers.CharField()
    paymentStatus=serializers.CharField()
    how=serializers.CharField()
    special_instruction=serializers.CharField()
    schedule_date=serializers.CharField()
    schedule_time=serializers.CharField()
    class Meta:
        model=Order
        fields=['user_phone_number','restaurant','phone_number','item_jsons','name','email',
        'shipping_address','billing_address','state','country','zip_code','total_price',
        'paymentStatus','how','special_instruction','schedule_date','schedule_time']



class UserAddressSerializer(ModelSerializer):
    user_phone_number=serializers.IntegerField()

    class Meta:
        model=Address
        fields=['user_phone_number']


class DeleteUserAddressSerializer(ModelSerializer):
    user_phone_number=serializers.IntegerField()
    address=serializers.CharField()


    class Meta:
        model=Address
        fields=['user_phone_number','address']


class AddUserAddressSerializer(ModelSerializer):
    shipping_address = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()
    zip_code = serializers.CharField()
    user_phone_number=serializers.IntegerField()

    class Meta:
        model = Address
        fields = ['shipping_address','state','country','zip_code','user_phone_number']


class OrderHistorySerializer(ModelSerializer):
    phone_number=serializers.IntegerField()

    class Meta:
        model=Order
        fields=['phone_number']

class OrderStatusSerializer(ModelSerializer):
    order_id=serializers.IntegerField()

    class Meta:
        model=Order
        fields=['order_id']

class CancelOrderStatusSerializer(ModelSerializer):
    order_id=serializers.IntegerField()

    class Meta:
        model=Order
        fields=['order_id']


class ChatbotUrlSerializer(serializers.Serializer):
    restaurant_name=serializers.CharField()
    item_jsons=serializers.CharField()
    how = serializers.CharField()
    session_id=serializers.CharField()


class PaymentStatusSerializer(ModelSerializer):
    order_id=serializers.CharField()
    payment_status=serializers.CharField()
    payment_mode=serializers.CharField()

    class Meta:
        model=Order
        fields=['order_id','payment_mode','payment_status']


class BookTableSerializer(ModelSerializer):
    restaurant=serializers.CharField()
    user_name=serializers.CharField()
    user_email=serializers.EmailField()
    user_phone_number=serializers.IntegerField()
    date=serializers.DateField()
    time=serializers.TimeField()
    number_of_people=serializers.IntegerField()
    message=serializers.CharField()

    class Meta:
        model=BookTable
        fields=['restaurant','user_name','user_email','user_phone_number','date','time','number_of_people','message']


class FeedbackSerializer(ModelSerializer):
    message=serializers.CharField()
    category=serializers.CharField()
    fb_type=serializers.CharField()
    

    class Meta:
        model=Feedback
        fields=['message','category','fb_type']


class RestaurantFromCitySerializer(ModelSerializer):
    city=serializers.CharField()

    class Meta:
        model=Restaurant
        fields=['city']