import datetime
import re
import time

from django.http import HttpResponse, JsonResponse

from .models import City, Street, Shop
from django.views.decorators.csrf import csrf_exempt

import json


def handler400(request, *args, **argv):
    return HttpResponse("Error",status=400)


def ReturnError(text: str) -> JsonResponse:
    """Функция возрата ошибки
    :param text Текст ошибки"""
    return JsonResponse({'Error': f'{text}'}, status=400, safe=False, json_dumps_params={'ensure_ascii': False}, content_type='application/json')


@csrf_exempt
def AddShop(request):
    """Функция добавления магазина"""
    data = json.loads(request.body)
    # Валидация данных
    # Проверка наличия ключей
    for key in ['name', 'city', 'street', 'house_number', 'time_open', 'time_close']:
        if key not in data.keys():
            return ReturnError(f'Key {key} not finded.')
    # Проверка не пуст ли ключ
    for el in ['name', 'city', 'street', 'house_number', 'time_open', 'time_close']:
        if not data[el]:
            return ReturnError(f"Value with key {el} is empty.")
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
    if len(Shop.objects.filter(name=data['name'], id_city=id_city, id_street=id_street, house_number=data['house_number'])) > 0:
        return ReturnError(f"This store already exists.")

    # Добавление магазина
    new_shop = Shop(name=data['name'], id_city=have_city[0], id_street=have_street[0], house_number=data['house_number'], time_open=data['time_open'],
                    time_close=data['time_close'])
    new_shop.save()

    return JsonResponse({"Response": f"{new_shop.id}"}, status=200, content_type='application/json')


@csrf_exempt
def GetCitiesView(request):
    """Функция возращает JSON со всеми городами. Доступные параметры запроса: order (name,-name,id,-id); page (N)"""
    if request.method != "GET":
        return ReturnError(f"Method {request.method} not allowed.")

    # Нумерация страниц, в противном случае вернёт все города
    if request.GET.get('page') and request.GET.get("page").isdigit() and int(request.GET.get("page")) > 0:
        lim = 10
        offset = (int(request.GET.get('page')) - 1) * lim

    else:
        lim = 1000000
        offset = 0
    # Сортировка
    ord = request.GET.get('order') if request.GET.get('order') and request.GET.get('order') in ['name', '-name', '-id', 'id'] else "id"

    # Запрос городов
    data = [{"id": i[0], "name": i[1]} for i in list(City.objects.values().values_list('id', 'name').order_by(ord)[offset:lim + offset])]
    return JsonResponse({"Response": data}, safe=False, json_dumps_params={'ensure_ascii': False}, content_type='application/json')


@csrf_exempt
def GetStreets(request, city):
    """Функция возращает улицы выбранного города. Доступные параметры запроса: order (name,-name,id,-id); page (N)"""
    # Проверка на наличие города в базе, а так же конвертация Текстового варианта в ID
    if not city.isdigit():
        list_city = City.objects.filter(name=city)
        if len(list_city) == 0:
            return ReturnError(f"The city of {city} is missing from the database.")
        city = list_city[0].id

    if len(City.objects.filter(id=int(city))) == 0:
        return ReturnError(f"There is no city with such an ID.")

    # Нумерация страниц, в противном случае вернёт все улицы
    if request.GET.get('page') and request.GET.get("page").isdigit() and int(request.GET.get("page")) > 0:
        lim = 10
        offset = (int(request.GET.get('page')) - 1) * lim

    else:
        lim = 1000000
        offset = 0
    # Сортировка
    ord = request.GET.get('order') if request.GET.get('order') and request.GET.get('order') in ['name', '-name', '-id', 'id'] else "id"

    # Запрос
    data = [{"id": i[0], "name": i[1]} for i in list(Street.objects.filter(id_city=city).values_list('id', 'name').order_by(ord)[offset:lim + offset])]

    return JsonResponse({"Response": data}, safe=False, json_dumps_params={'ensure_ascii': False}, status=200, content_type='application/json')


def ConvertTime(time: str):
    """Функция перевода времени формата HH:MM:SS в секунды"""
    sp = time.split(":")
    return int(sp[0]) * 60 * 60 + int(sp[1]) * 60 + int(sp[2])


@csrf_exempt
def GetShops(request):
    """Функция получения магазинов.
    :param open открыт ли в данный момент магазин
    :param street Вернёт магазины данной улицы
    :param city Вернёт магазины данного города
    :param order Сортировка
    :param page Страница"""
    # Нумерация
    if request.GET.get('page') and request.GET.get("page").isdigit() and int(request.GET.get("page")) > 0:
        lim = 10
        offset = (int(request.GET.get('page')) - 1) * lim

    else:
        lim = 1000000
        offset = 0
    # Сортировка
    ord = request.GET.get('order') if request.GET.get('order') and request.GET.get('order') in ['name', '-name', '-id', 'id'] else "id"

    # Запрос всех магазинов (В случае если использовать чистый SQL возможно реализовать в разы "быстрее")
    tmp = Shop.objects.all().order_by(ord)

    # При наличии ID города, отберёт нужные магазины
    if request.GET.get('city') and request.GET.get('city').isdigit():
        tmp = tmp.filter(id_city=int(request.GET.get('city')))
    # При наличии ID улицы, отберёт нужные магазины
    if request.GET.get('street') and request.GET.get('street').isdigit():
        tmp = tmp.filter(id_street=int(request.GET.get('street')))

    # При наличии Статуса открытия, отберёт нужные магазины
    if request.GET.get('open') and request.GET.get('open') in ['1', '0']:
        # Весьма костыльная функция, единственный момент над которым я думал долго, но не придумал рационального решения
        open_stat = {"status": int(request.GET.get('open')), 'mass': []}
        n_t = ConvertTime(time.strftime("%H:%M:%S", time.gmtime(time.time())))
        for elem in tmp.values():
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
            tmp = tmp.exclude(id=ids)

    data = [{'id': i[0], 'name': i[1], 'street': i[2], 'city': i[3], 'house_number': i[4], 'time_open': i[5], 'time_close': i[6]} for i in
            list(tmp.values_list('id', 'name', 'id_street__name', 'id_city__name', 'house_number', 'time_open', 'time_close').order_by(ord)[offset:lim + offset])]

    return JsonResponse({"Response": data}, safe=False, json_dumps_params={'ensure_ascii': False}, status=200, content_type='application/json')


@csrf_exempt
def ChoiseMethodShop(request):
    """Функция выбора зависящая от метода"""
    if request.method == "POST":
        return AddShop(request)
    elif request.method == "GET":
        return GetShops(request)
    else:
        return ReturnError(f"Method {request.method} not allowed.")
