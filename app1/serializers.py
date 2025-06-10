from rest_framework import serializers
from .models import AccUsers

class AccUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccUsers
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=30)
    password = serializers.CharField(max_length=100, write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if not username or not password:
            raise serializers.ValidationError('Username and password are required.')
        
        return attrs