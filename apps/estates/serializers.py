from rest_framework import serializers
from .models import VisitorToken, Estate, Apartment


class EstateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estate
        fields = '__all__'


class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = '__all__'


class GenerateTokenSerializer(serializers.Serializer):
    visitor_name = serializers.CharField(required=True)
    visitor_phone = serializers.CharField(required=False, allow_blank=True)
    visitor_email = serializers.EmailField(required=False, allow_blank=True)
    expiration = serializers.IntegerField(required=True, min_value=1)

    def validate(self, data):
        if not data.get('visitor_phone') and not data.get('visitor_email'):
            raise serializers.ValidationError("Either phone or email must be provided")
        return data