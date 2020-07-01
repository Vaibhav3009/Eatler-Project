from django.urls import path
from accounts.api import views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    # path('hello/', views.HelloView.as_view(), name='hello'),
    path('generate/',views.otp.as_view(), name="generate"),
    path('register/',views.register.as_view(), name="register"),
    path('login/',views.login.as_view(),name="login"),
    path('generate_with_param/',views.otp_with_param.as_view(),name="generate_with_param"),

    # path('validate/', ValidateOTP.as_view(), name="validate"),
]

# phone number ->otp jayega->otp verify->token return (Login)

# phone_number/full name/country_code/ ->otp bhejega->otp verify -> databases me save karna
