from django.conf.urls import url
from .views import homepage
from django.urls import path
# from .views import ProductFormView,RestaurantFormView
from .views import (RestaurantCreateView,RestaurantListView,RestaurantDetailView,RestaurantUpdateView,
                    RestaurantDeleteView,ProductCreateView,ProductUpdateView,ProductDeleteView,
                    MenuView,RestaurantMenuView,DeliveryMenuView,CheckoutView,CheckoutTakeawayView,handleRequest,integration,
                    updateStatus,chatbotCheckout,sendEmail,checkNumber,verifyOTP,ProfileView,DeleteAddress,BookTableView,
                    getFeedback)
app_name='main'

urlpatterns = [
    path('',homepage,name='homepage'),
    # path('add_product/',ProductFormView,name="add_product"),
    # path('add_restaurant/',RestaurantFormView,name="add_restaurant"),
    path('list/',RestaurantListView.as_view(),name="list_restaurant"),
    path('create/',RestaurantCreateView.as_view(),name="create_restaurant"),
    path('list/<int:pk>',RestaurantDetailView.as_view(),name="detail_restaurant"),
    path("update/<int:pk>/",RestaurantUpdateView.as_view(),name="update_restaurant"),
    path("delete/<int:pk>/",RestaurantDeleteView.as_view(),name="delete_restaurant"),

    path('<int:pk>/create_product/',ProductCreateView.as_view(),name="create_product"),
    path('update_product/<int:pk>',ProductUpdateView.as_view(),name="update_product"),
    path('delete_product/<int:pk>',ProductDeleteView.as_view(),name="delete_product"),

    path('menu/',MenuView,name="menu"),
    path('menu/<int:pk>/',RestaurantMenuView,name="restaurant_menu"),

    path('delivery_menu/',DeliveryMenuView,name="delivery_menu"),

    path('checkout/',CheckoutView,name="checkout_url"),

    path('checkout_takeaway/',CheckoutTakeawayView,name="checkout_takeaway_url"),

    path('handleRequest/',handleRequest,name='handleRequest'),



    path('integration/',integration,name='integration'),

    path('updateStatus/',updateStatus,name='updateStatus'),
    path('chatbotCheckout/',chatbotCheckout,name='chatbotCheckout'),
    # path('orderStatus/<int:order_id>',orderStatus,name='orderStatus'),
    path('sendemail/',sendEmail,name='sendemail'),
    path('sendfeedback/',getFeedback,name='sendfeedback'),


    path('check_number/',checkNumber,name='check_number'),
    path('verify_otp_number/',verifyOTP,name='verify_otp_number'),


    path('profile/',ProfileView,name="user_profile"),
    path('deleteAddress/',DeleteAddress,name="deleteAddress"),
    
    path('bookTable/',BookTableView,name="bookTable"),
    






]
