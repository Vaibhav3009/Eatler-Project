from django.shortcuts import render, HttpResponse, redirect
from django.views.generic import (TemplateView, FormView)
from django.views import View
from django.contrib.auth import authenticate, login,logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
import json
from django.shortcuts import get_object_or_404
from .forms import RegisterForm, LoginForm, PhoneVerificationForm
from .authy_api import send_verfication_code, verify_sent_code
from .models import User
from django.contrib.auth.models import Group
from .decorators import allowed_users



from main.models import Restaurant,Product,Order





class IndexView(TemplateView):

    template_name = 'accounts/index.html'


class RegisterView(SuccessMessageMixin, FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_message = "One-Time password sent to your registered mobile number.\
                        The verification code is valid for 10 minutes."

    def form_valid(self, form):

        user=self.request.POST
        try:
            response = send_verfication_code(user)
        except Exception as e:
            messages.add_message(self.request, messages.ERROR,
                                'verification code not sent. \n'
                                'Please re-register.')
            return redirect('/register')
        data = json.loads(response.text)
        if data['success'] == False:
            messages.add_message(self.request, messages.ERROR,
                            data['message'])
            return redirect('/register')

        else:
            kwargs = {'userr': user}
            return render(self.request,'accounts/phone_confirm.html',kwargs)


def resend_url(request,phone_number,country_code,full_name):

    user={"phone_number":phone_number,"country_code":country_code,"full_name":full_name}
    print(user)
    try:
        response = send_verfication_code(user)
        pass
    except Exception as e:
        messages.add_message(request, messages.ERROR,
                'verification code not sent. \n'
                )
        return redirect('/login')
    data = json.loads(response.text)

    if data['success'] == False:
        messages.add_message(request, messages.ERROR,
        data['message'])
        return redirect('/login')

    if data['success'] == True:
        # request.method = "GET"
        kwargs = {'userr':user}
        return render(request,'accounts/phone_confirm.html',kwargs)
        # return PhoneVerificationView(request,**kwargs)


def LoginView(request):
    template_name='accounts/login.html'
    if request.method == "POST":
        user=request.POST
        userob = User.objects.filter(phone_number=user['phone_number'])
        if userob:
            try:
                auser={'phone_number':user['phone_number'],'country_code':user['country_code']}
                response = send_verfication_code(auser)
                pass
            except Exception as e:
                messages.add_message(request, messages.ERROR,
                        'verification code not sent. \n'
                        'Please retry logging in.')
                return redirect('/login_verify')
            data = json.loads(response.text)

            if data['success'] == False:
                    print("If verifiacation code is not sent by twilio")
                    messages.add_message(request, messages.ERROR,
                    data['message'])
                    return redirect('/login_verify')

            print(user)
            if data['success'] == True:
                print("if verification code is sent by twilio")

                user_phone_number= user['phone_number']
                user_country_code= user['country_code']
                userr={'phone_number':user_phone_number ,'country_code':user_country_code,'full_name':"user"}
                # return PhoneVerificationView(request,**kwarg)
                print(userr)
                print("checking")
                using={'userr':userr}
                return render(request,'accounts/phone_confirm.html',using)
            else:
                messages.add_message(request, messages.ERROR,
                data['message'])
                return redirect('/login')
        else:
            messages.add_message(request, messages.ERROR,
                    'User does not exist. \n'
                    'Please register.')
            return redirect('/register')

    else:
        if request.user.is_authenticated:
            return redirect('/')
        return render(request,'accounts/login.html')









def PhoneVerificationView(request,phone_number,country_code,full_name):
    template_name = 'accounts/phone_confirm.html'
    user={"phone_number":phone_number,"country_code":country_code,"full_name":full_name}
    if request.method == "POST":
        form = PhoneVerificationForm(request.POST)
        if form.is_valid():
            verification_code = request.POST['one_time_password']
            response = verify_sent_code(verification_code, user)
            data = json.loads(response.text)
            if data['success'] == True:
                try:
                    already=User.objects.get(phone_number=user['phone_number'])
                except:
                    already=None
                if already:
                    login(request, already)
                    if already.groups.filter(name='restaurant').exists():
                        return redirect('/restaurant')
                    return redirect('/index')
                else:
                    userob=User.objects.create(full_name=user['full_name'],
                                            phone_number=user['phone_number'],
                                            country_code=user['country_code'])
                    group = Group.objects.get(name='customer')
                    userob.groups.add(group)
                    login(request, userob)
                    return redirect('/index')
            else:
                messages.add_message(request, messages.ERROR,
                                data['message'])
                using={'userr':user}
                return render(request,'accounts/phone_confirm.html',using)

        else:
            using={'userr':user}
            return render(request,'accounts/phone_confirm.html',using)
    elif request.method == "GET":
        using={'userr':user}
        return render(request,'accounts/phone_confirm.html',using)



@login_required
def user_logout(request):
    logout(request)
    global user_for_phone_confirmation
    user_for_phone_confirmation={}
    return redirect('/')





@method_decorator(login_required(login_url="/login/"), name='dispatch')
class DashboardView(SuccessMessageMixin, View):
    template_name = 'accounts/dashboard.html'

    def get(self, request):
        context = {
            'user':self.request.user,
            }
        return render(self.request, self.template_name, {})


@login_required
@allowed_users(allowed_roles=['restaurant'])
def RestaurantView(request):
    template_name="accounts/restaurant.html"
    user=request.user
    restaurant_list=Restaurant.objects.filter(user=user)
    order={}
    product_list={}
    counter={'pending':0,'confirm':0,'cancel':0,'out_for_delivery':0,'delivered':0,'all_orders':0}
    for restaurant in restaurant_list:
        order_list=Order.objects.filter(restaurant=restaurant).order_by('order_date')


        i=1

        order[restaurant.name]={}
        for item in order_list:

            temp_product_list={}
            item_jsons = item.item_jsons.replace("\'", "\"")
            item_jsons=json.loads(item_jsons)
            if item.order_status=='pending':
                counter['pending']=counter['pending']+1
            elif item.order_status=='confirm':
                counter['confirm']=counter['confirm']+1
            elif item.order_status=='cancel':
                counter['cancel']=counter['cancel']+1
            elif item.order_status=='out_for_delivery':
                counter['out_for_delivery']=counter['out_for_delivery']+1
            elif item.order_status=='delivered':
                counter['delivered']=counter['delivered']+1


            for product in item_jsons:
                temp_product_list[product]={'product_name':item_jsons[product][1],
                                        'quantity':item_jsons[product][0],
                                        'price':item_jsons[product][2],
                                        'add_on1':item_jsons[product][3],
                                        'add_on2':item_jsons[product][4],
                                        'add_on3':item_jsons[product][5],
                                        'add_on4':item_jsons[product][6],
                                        'add_on5':item_jsons[product][7],}
            product_list[item.order_id]=temp_product_list
            order[restaurant.name][i]={'order_id':item.order_id,'amount':item.total_price,'order_time':item.order_time,
                                        'order_date':item.order_date,'order_status':item.order_status}
            i=i+1

    counter['all_orders']=counter['pending']+counter['confirm']+counter['cancel']+counter['delivered']+counter['out_for_delivery']
    product_dict=json.dumps(product_list,default=str)
    return render(request,template_name,context={'order':order,'product_dict':product_dict,'counter':counter})




# @method_decorator(login_required(login_url="/login/"),name='dispatch')
# @method_decorator(allowed_users(allowed_roles=['restaurant']),name='dispatch')
# class RestaurantView(LoginRequiredMixin,View):
#     template_name="accounts/restaurant.html"
#
#     def get(self,request):
#
#         # restaurant_owner=User.objects.filter(request.user)
#         return render(self.request,self.template_name)   #{'user':restaurant_owner}
