from datetime import date

from rest_framework import serializers

from .models import City, Street, Shop


class CitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class StreetsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Street
        fields = ['id', 'name']


class ShopSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='id_city.name')
    street_name = serializers.CharField(source='id_street.name')

    class Meta:
        model = Shop
        fields = ["id", "name", "city_name", "street_name", "house_number", "time_open", "time_close"]
