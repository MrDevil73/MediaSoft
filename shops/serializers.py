from datetime import date

from django.core.validators import MaxValueValidator

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator


from .models import City,Street,Shop

class ShopSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    id_city = serializers.CharField(max_length=100)
    id_street = serializers.CharField(max_length=100)
    house_number = serializers.CharField(max_length=100)
    time_open = serializers.TimeField(
        format="%H:%M",
    )
    time_close = serializers.TimeField(
        format="%H:%M",
    )

    class Meta:
        validators = [

        ]

    def validate(self, attrs):
        #На данном этапе я пытался сделать чтобы передавать именно название города и улицы, а не их айди, но увы, мои знания Сериализации меня остановили

        _city=attrs['id_city']
        have_city=City.objects.filter(id=_city)

        if len(have_city)==0:
            raise ValidationError("Данного города нет в базе",code="City absent")
        _street=attrs['id_street']

        have_street = Street.objects.filter(id=_street,id_city=have_city[0]).select_related()
        if len(have_street) == 0:
            raise ValidationError("Данной улицы нет в указанном городе", code="Street absent")


        return attrs

    def create(self, validated_data):

        return Shop.objects.create(**validated_data)
