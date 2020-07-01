from django.urls import path
from main.api import views
from rest_framework.authtoken.views import obtain_auth_token





urlpatterns = [
    # path('hello/', views.HelloView.as_view(), name='hello'),
    path('query/',views.getQuery.as_view(), name="query"),
    path('product/',views.getProduct_without_param.as_view(), name="product_list"),
    path('product_android/',views.getProduct_without_param_android.as_view(), name="product_list_android"),
    path('product_get/',views.getProduct_with_param.as_view(), name="product_list_get"),
    path('address/',views.getCoordinates.as_view(), name="coordinates"),
    path('nearbyRestaurant/',views.getNearbyRestaurant_without_param.as_view(), name="nearbyRestaurant"),
    path('nearbyRestaurant_get/',views.getNearbyRestaurant_with_param.as_view(), name="nearbyRestaurant_get"),
    path('chatbot/',views.chatbot_integration_API.as_view(), name="chatbot"),
    path('orderdetails/',views.OrderDetails.as_view(), name="orderdetails"),
    path('userAddress/',views.getUserAddress.as_view(), name="userAddress"),
    path('deleteuserAddress/',views.deleteUserAddress.as_view(), name="deleteuserAddress"),
    path('adduserAddress/',views.AddUserAddress.as_view(), name="adduserAddress"),
    path('orderhistory/',views.OrdersHistory.as_view(), name="orderhistory"),
    path('orderstatus/',views.getOrderStatus.as_view(), name="orderstatus"),
    path('cancelorder/',views.cancelOrder.as_view(), name="cancelorder"),



    path('chatboturl/',views.Chatboturl.as_view(), name="chatboturl"),
    path('paymentStatus/',views.getPaymentStatus.as_view(), name="paymentStatus"),
    path('bookTable/',views.BookTableAPI.as_view(), name="bookTable"),
    path('getFeedback/',views.FeedbackAPI.as_view(), name="getFeedback"),

    path('restaurantFromCity/',views.getRestaurantFromCity.as_view(), name="restaurantFromCity"),

    # path('login/',views.login.as_view(),name="login"),

    # path('validate/', ValidateOTP.as_view(), name="validate"),
]
