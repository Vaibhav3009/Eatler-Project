from datetime import date
from django.db import models
from django.contrib.auth.models import PermissionsMixin, AbstractUser
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _

from django.contrib.auth.models import UserManager
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

class UserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, phone_number,password=None, **extra_fields):   #remove password

        if not phone_number:
            raise ValueError('The given phone number must be set')
        user = self.model(phone_number=phone_number,password=password, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, **extra_fields):   # password=None
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(phone_number,password, **extra_fields)

    def create_superuser(self, phone_number,password=None, **extra_fields):    #remove password
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(phone_number,password,  **extra_fields)   #remove password


class User(AbstractBaseUser, PermissionsMixin):
    # username = models.CharField(_('username'), max_length=130, unique=True)
    full_name = models.CharField(_('full name'), max_length=130, blank=True)
    is_staff = models.BooleanField(_('is_staff'), default=False)
    is_active = models.BooleanField(_('is_active'), default=True)
    date_joined = models.DateField(_("date_joined"), default=date.today)
    # phone_number_verified = models.BooleanField(default=False)
    # change_pw = models.BooleanField(default=True)
    phone_number = models.IntegerField(unique=True)
    country_code = models.IntegerField()
    # two_factor_auth = models.BooleanField(default=False)
    password=models.CharField(blank=True,max_length=100)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['full_name', 'country_code']

    class Meta:
        # ordering = ('username',)
        verbose_name = _('user')
        verbose_name_plural = _('users')

    

    def get_short_name(self):
        """
        Returns the display name.
        If full name is present then return full name as display name
        else return username.
        """
        if self.full_name != '':
            return self.full_name
        else:
            return self.phone_number


    def __str__(self):

        return self.full_name

    def get_model_fields(self):
        return self._meta.fields

@receiver(post_save,sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender,instance=None,created=False,**kwargs):
    if created:
        Token.objects.create(user=instance)





