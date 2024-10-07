from django.contrib.auth import get_user_model
from rest_framework import serializers


class UserRegistrationSerializer(serializers.ModelSerializer):
    '''
    Serializer for user registration, handling validation and user creation.

    Attributes:
        password (str): The user's password.
        confirm_password (str): The user's password confirmation.
        email (str): The user's email address.
        mobile_number (str): The user's mobile number.

    Validations:
        - The password and confirm_password fields must match.
        - The email must be unique.
        - The email must be a valid email address (email field validation).

    '''
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'confirm_password', 'mobile_number']

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        user = get_user_model()(**validated_data)
        user.set_password(validated_data['password'])  # Hash the password
        user.save()
        return user

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return attrs

    def validate_email(self, value):
        if get_user_model().objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value


class UserListSerializer(serializers.ModelSerializer):
    '''
    Used as a nested serializer to display user details in other serializers.
    '''

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'mobile_number']
