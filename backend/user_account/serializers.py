from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser,Cheque
from django.db import IntegrityError


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    def validate_account_number(self, value):
        if CustomUser.objects.filter(account_number=value).exists():
            raise serializers.ValidationError('User with this account number already exists')
        return value
    
    def validate_password(self, value):
        if not value:
            raise serializers.ValidationError('Pin required!', code='required')
        if not value.isdigit():
            raise serializers.ValidationError('Pin must be a numeric', code='invalid')
        if len(value) != 4:
            raise serializers.ValidationError('Pin must be 4 digits only', code='length_error')
        return make_password(value)  

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'account_number', 'balance', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        try:
            return super().create(validated_data)
        except IntegrityError as e:
            print(e)  # Print the details of the IntegrityError
            raise serializers.ValidationError('An error occurred while creating the user. Please try again.')

class LoginSerializer(serializers.Serializer):
    account_number = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        account_number = attrs.get('account_number')
        password = attrs.get('password')

        if account_number and password:
            user = CustomUser.objects.filter(account_number=account_number).first()
            if user and user.check_password(password):
                return user
            raise AuthenticationFailed('Invalid account number or pin.')
        else:
            raise AuthenticationFailed('Must include "account_number" and "pin".')


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['access'] = serializers.CharField(read_only=True)
        self.fields['refresh'] = serializers.CharField(read_only=True)


class ChangePasswordSerializer(serializers.Serializer):
    old_pin = serializers.CharField(required=True)
    new_pin1 = serializers.CharField(required=True)
    new_pin2 = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_pin1'] != data['new_pin2']:
            raise serializers.ValidationError("The two new pins don't match")
        return data
    
    
class ChequeSerializer(serializers.ModelSerializer):
    cheque_number = serializers.CharField(required=True)
    class Meta:
        model = Cheque
        fields = ['cheque_number', 'status']    