"""
users/serializers.py

Serializers for Django's built-in User model.
Password is always write-only — never returned in any response.
"""

from django.contrib.auth.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Read-only serializer returned after login, register, and GET /auth/me/.

    Output fields:
        id          -- database pk
        username    -- login name
        email       -- may be empty string if not provided at registration
        date_joined -- ISO 8601 timestamp
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class RegisterSerializer(serializers.ModelSerializer):
    """
    Write-only serializer used by RegisterView to create a new user account.

    Input fields:
        username (str)          -- must be unique; validated by Django User model
        email    (str, optional)-- stored but not verified
        password (str)          -- minimum 8 characters; hashed via create_user()

    The password field is marked write_only=True so it is never echoed back
    in any response. create() delegates to User.objects.create_user() which
    handles password hashing automatically.
    """
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        """Creates and returns a new User with a hashed password."""
        return User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
        )
