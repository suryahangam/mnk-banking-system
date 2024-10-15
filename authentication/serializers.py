from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework.validators import UniqueValidator


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
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=get_user_model().objects.all(),
                message="Email already exists."
            )
        ]
    )
    password = serializers.CharField(
        write_only=True, validators=[validate_password])
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



class UserListSerializer(serializers.ModelSerializer):
    '''
    Used as a nested serializer to display user details in other serializers.
    '''

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'mobile_number']
