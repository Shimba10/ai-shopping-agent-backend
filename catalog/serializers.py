from rest_framework import serializers
from .models import Phone

class PhoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = '__all__'

class SimpleProductCardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phone
        fields = ['id', 'brand', 'model', 'price_inr', 'camera_mp', 'battery_mah', 'fast_charge_w', 'compact']
