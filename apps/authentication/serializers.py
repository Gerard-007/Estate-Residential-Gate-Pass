from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=11)
    password = serializers.CharField(write_only=True)
    status = serializers.ChoiceField(
        choices=User.STATUS,
        required=False,
        default="Visitor"
    )

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already in use.")
        return value

    def validate_phone(self, value):
        if len(value) != 11:
            raise serializers.ValidationError("Phone number must be 11 digits")
        return value

class TokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.CharField()
