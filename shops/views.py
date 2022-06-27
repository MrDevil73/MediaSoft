import datetime
import re
import time
import json

from django.http import HttpResponse, JsonResponse

from .models import City, Street, Shop
from django.views.decorators.csrf import csrf_exempt

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import ValidationError

from django.core import serializers

from . import serializers as ser

PAGE_SIZE = 5


def handler400(request, *args, **argv):
    return HttpResponse("Error", status=400)


def ReturnError(text: str) -> JsonResponse:
    """Функция возрата ошибки
    :param text Текст ошибки"""
    return JsonResponse({'Error': f'{text}'}, status=400, safe=False, json_dumps_params={'ensure_ascii': False}, content_type='application/json')


class GetCitiViews(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    query = City.objects.all()

    @action(detail=True, methods=['get'])
    def getAllCity(self, request):
        """Функция возращает все города. Доступные параметры запроса: order (name,-name,id,-id); page (N)"""
        if request.GET.get('order') and request.GET.get("order") in ["id", "-id", "name", "-name"]:
            self.query = self.query.order_by(request.GET.get('order'))
        if request.GET.get('page') and int(request.GET.get('page')):
            _page = int(request.GET.get('page')) - 1 if int(request.GET.get('page')) > 0 else 0
            self.query = self.query[PAGE_SIZE * _page:PAGE_SIZE * (_page + 1)]
        ser_data = ser.CitiesSerializer(self.query, many=True)
        return Response({"cities": ser_data.data})


class StreetsView(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    query = Street.objects.all()

    @action(detail=True, methods=['get'])
    def getStreers(self, request, id_city_url):
        """Функция возращает улицы выбранного города. Доступные параметры запроса: order (name,-name,id,-id); page (N)"""
        if not id_city_url.isdigit():
            return ReturnError("This city is missing.")

        if len(self.query.filter(id_city=id_city_url)) < 1:
            return ReturnError("This city is missing.")
        self.query = self.query.filter(id_city=id_city_url)

        if request.GET.get('order') and request.GET.get("order") in ["id", "-id", "name", "-name"]:
            self.query = self.query.order_by(request.GET.get('order'))
        if request.GET.get('page') and int(request.GET.get('page')):
            _page = int(request.GET.get('page')) - 1 if int(request.GET.get('page')) > 0 else 0
            self.query = self.query[PAGE_SIZE * _page:PAGE_SIZE * (_page + 1)]

        ser_data = ser.StreetsSerializer(self.query, many=True)
        return Response({"streets": ser_data.data, "city_id": int(id_city_url)})


def ConvertTime(time: str):
    """Функция перевода времени формата HH:MM:SS в секунды"""
    sp = time.split(":")
    return int(sp[0]) * 60 * 60 + int(sp[1]) * 60 + int(sp[2])


class ShopView(viewsets.ModelViewSet):
    renderer_classes = [JSONRenderer]
    tmp = Shop.objects.all()
    serializer_class = ser.ShopSerializer

    @action(detail=True, methods=['get'])
    def getShops(self, request):
        """Функция получения магазинов.
        :param open открыт ли в данный момент магазин
        :param street Вернёт магазины данной улицы
        :param city Вернёт магазины данного города
        :param order Сортировка
        :param page Страница
        Возвращет массив магазинов."""
        params = [request.GET.get(i) if bool(request.GET.get(i)) else None for i in ["open", "street", "city", "order", "page"]]
        # Фильтр города
        if params[2] and params[2].isdigit():
            self.tmp = self.tmp.filter(id_city=int(params[2]))
        # При наличии ID улицы, отберёт нужные магазины
        if params[1] and params[1].isdigit():
            self.tmp = self.tmp.filter(id_street=int(params[1]))

        # Блок обработки статуса "открыто/закрыто"
        if params[0] in ['1', '0']:
            # Весьма костыльная функция, единственный момент над которым я думал долго, но не придумал рационального решения

            # Альтернатива ей, но она будет возращать чаще не верно
            # if params[0]=="1":
            #     self.tmp=self.tmp.exclude(time_open__lte=,time_close__gte=time.strftime("%H:%M:%S", time.gmtime(time.time())))
            # else:
            #     self.tmp=self.tmp.filter(time_open__lte="22:25:00",time_close__gte=time.strftime("%H:%M:%S", time.gmtime(time.time())))

            open_stat = {"status": int(params[0]), 'mass': []}
            n_t = ConvertTime(time.strftime("%H:%M:%S", time.gmtime(time.time())))
            for elem in self.tmp.values():
                t_o, t_c = ConvertTime(str(elem['time_open'])), ConvertTime(str(elem['time_close']))
                if t_o == t_c:
                    if open_stat['status'] == 0:
                        open_stat['mass'].append(elem['id'])
                elif t_o > t_c:
                    if n_t in list(range(t_o, 86399)) + list(range(0, t_c)):
                        if open_stat['status'] == 0:
                            open_stat['mass'].append(elem['id'])
                    elif open_stat['status'] == 1:
                        open_stat['mass'].append(elem['id'])
                else:
                    if n_t > t_o and n_t < t_c:
                        if open_stat['status'] == 0:
                            open_stat['mass'].append(elem['id'])
                    elif open_stat['status'] == 1:
                        open_stat['mass'].append(elem['id'])

            # Удаление всех "лишних" магазинов
            for ids in open_stat['mass']:
                self.tmp = self.tmp.exclude(id=ids)

        # Сортировка
        if params[3] in ["id", "-id", "name", "-name"]:
            self.tmp = self.tmp.order_by(request.GET.get('order'))
        # Пагинация
        if params[4] and params[4].isdigit():
            _page = int(params[4]) - 1 if int(params[4]) > 0 else 0
            self.tmp = self.tmp[PAGE_SIZE * _page:PAGE_SIZE * (_page + 1)]

        return Response({"shops": ser.ShopSerializer(self.tmp, many=True).data})

    def addShop(self, request):
        """Функция добавления магазина
        Получает Json-объект с ключами :'name', 'city', 'street', 'house_number', 'time_open', 'time_close'
        Возращает id созданного магазина, или ошибку"""
        data = json.loads(request.body)
        # Валидация данных
        # Проверка наличия ключей и Проверка не пуст ли ключ
        for key in ['name', 'city', 'street', 'house_number', 'time_open', 'time_close']:
            if key not in data.keys() or not data[key]:
                return ReturnError(f'Key {key} not finded or he is empty.')
        # Проверка корректности ввода даты
        if not re.match(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", data['time_open']) or not re.match(r"^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$", data['time_close']):
            return ReturnError(f"Incorrect time format. Use HH:MM.")

        # Проверка на наличие города в базе
        have_city = City.objects.filter(name=data['city']) if not data['city'].isdigit() else City.objects.filter(id=int(data['city']))
        if len(have_city) == 0:
            return ReturnError(f"The city of {data['city']} is missing from the database.")

        # Проверка на наличие улицы данного города в базе
        have_street = Street.objects.filter(name=data['street'], id_city=have_city[0].id) if not data['street'].isdigit() else Street.objects.filter(id=int(data['street']),
                                                                                                                                                     id_city=have_city[0].id)
        if len(have_street) == 0:
            return ReturnError(f"{data['street']} street is missing in this city.")

        id_city, id_street = have_city[0].id, have_street[0].id
        # Проверка на наличие такого же магазина
        if len(self.tmp.filter(name=data['name'], id_city=id_city, id_street=id_street, house_number=data['house_number'])) > 0:
            return ReturnError(f"This store already exists.")

        # Добавление магазина
        new_shop = Shop(name=data['name'], id_city=have_city[0], id_street=have_street[0], house_number=data['house_number'], time_open=data['time_open'],
                        time_close=data['time_close'])
        new_shop.save()

        return Response({"Response": f"{new_shop.id}"})
