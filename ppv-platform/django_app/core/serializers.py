from rest_framework import serializers
from .models import User, Content, Payment, AccessToken

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'is_active', 'is_staff', 'date_joined']

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = ['id', 'title', 'description', 'file_url', 'price']

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'user', 'content', 'amount', 'status', 'reference', 'created_at']

class AccessTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccessToken
        fields = ['id', 'token', 'user', 'content', 'expires_at', 'max_uses', 'used_count', 'is_active']
