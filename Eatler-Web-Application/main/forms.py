from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.auth import authenticate
from .models import Product,Restaurant


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


class ProductForm(forms.ModelForm):



    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',}))
    short_description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',}))
    long_description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control',}))
    photo = forms.ImageField(required=False,widget=forms.FileInput(attrs={'class':'form-control-file',}))
    price = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control',}))
    add_on1 = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control',}))
    add_on2 = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control',}))
    add_on3 = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control',}))
    add_on4 = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control',}))
    add_on5 = forms.CharField(required=False,widget=forms.TextInput(attrs={'class':'form-control',}))
    type = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control',}),choices=TYPE)
    cuisine = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control',}),choices=CUISINE)
    category = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control',}),choices=CATEGORY)

    class Meta:
        model = Product
        exclude = ('restaurant','rating')



class RestaurantForm(forms.ModelForm):
   
   
    
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',},))
    short_description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control' }))
    long_description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    address = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    locality = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    city = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control'}))
    photo = forms.ImageField(widget=forms.FileInput(attrs={'class':'form-control-file'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    contact_number = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}))
    open_time=forms.TimeField(widget=forms.TimeInput(attrs={'class':'form-control'}))
    close_time=forms.TimeField(widget=forms.TimeInput(attrs={'class':'form-control'}))
    northindian=forms.BooleanField(initial=True,required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    southindian=forms.BooleanField(initial=True,required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    chinese=forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    continental=forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    oriental=forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    veg=forms.BooleanField(initial=True,required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    non_veg=forms.BooleanField(initial=False,required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    live_video=forms.URLField(widget=forms.URLInput(attrs={'class':'form-control'}))

    class Meta:
        model = Restaurant
        exclude = ('user','rating','latitude','longitude')











class RestaurantFormUpdate(forms.ModelForm):
   
    
    name = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control',},))
    short_description = forms.CharField(widget=forms.TextInput(attrs={'class':'form-control' }))
    long_description = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control'}))
    photo = forms.ImageField(required=False,widget=forms.FileInput(attrs={'class':'form-control-file',}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class':'form-control'}))
    contact_number = forms.IntegerField(widget=forms.NumberInput(attrs={'class':'form-control'}))
    open_time=forms.TimeField(widget=forms.TimeInput(attrs={'class':'form-control'}))
    close_time=forms.TimeField(widget=forms.TimeInput(attrs={'class':'form-control'}))
    northindian=forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    southindian=forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    chinese=forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    continental=forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    oriental=forms.BooleanField(required=False,widget=forms.CheckboxInput(attrs={'class':'form-check-input'}))
    live_video=forms.URLField(widget=forms.URLInput(attrs={'class':'form-control'}))


    class Meta:
        model = Restaurant
        exclude = ('user','rating','latitude','longitude','address','locality','city')


  