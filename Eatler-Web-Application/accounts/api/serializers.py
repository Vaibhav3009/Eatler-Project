from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from accounts.models import User
from phonenumber_field.formfields import PhoneNumberField


class OTPSerializer(ModelSerializer):
    phone_number = serializers.IntegerField()
    country_code = serializers.IntegerField()

    class Meta:
        model = User
        fields = ('phone_number','country_code')

class RegistrationSerializer(ModelSerializer):
    full_name = serializers.CharField()
    phone_number = serializers.IntegerField()
    country_code = serializers.IntegerField()
    otp = serializers.IntegerField()
    class Meta:
        model = User
        fields = ['full_name','phone_number','country_code','otp']

    def	save(self):
        user = User(
					full_name=self.validated_data['full_name'],
					phone_number=self.validated_data['phone_number'],
                    country_code=self.validated_data['country_code']
				)
        user.save()
        return user

class LoginSerializer(ModelSerializer):
    phone_number = serializers.IntegerField()
    country_code = serializers.IntegerField()
    otp = serializers.IntegerField()

    class Meta:
        model=User
        fields=['phone_number','country_code','otp']

	# def	save(self):
    #
	# 	user = User(
	# 				full_name=self.validated_data['full_name'],
	# 				phone_number=self.validated_data['phone_number'],
    #                 country_code=self.validated_data['country_code']
	# 			)
    #     otp =
    #     response = verify_sent_code(verification_code, user)
    #     print(response.text)
    #     data = json.loads(response.text)
    #
    #     if data['success'] == True:
    #
    #     else:
	# 		raise serializers.ValidationError({'OTP': 'Wrong OTP'})
	# 	account.set_password(password)
	# 	account.save()
	# 	return account
