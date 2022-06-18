# MediaSoft
<h2>Установка</h2>
<p>Скачать репозиторий<br> Создать виртуальное окружение<br> Установить необходимые библиотеки командой pip install -r requirements.txt<br> Запустить проект командой python manage.py runserver 0.0.0.0:8000</p>
<h3>Docker</h3>
docker-compose build<br>
docker-compose up<br>
И будет вам счастье :)

<h2>Методы</h2>
GET /city/ — получение списка городов из базы;

GET /city/city_id/street/ — получение списка улиц города (city_id — идентификатор города, или же его название);

GET /shop/?street={street_id}&city={city_id}&open=0/1 — получение списка магазинов; 
Метод принимает параметры для фильтрации. Параметры не обязательны. В случае отсутствия параметров выводятся все магазины, если хоть один параметр есть , то по         нему выполняется фильтрация. 

Каждый из GET методов поддноживает так же сортировку параметром "order" и имеет доступные значения : id,-id,name,-name. В качестве дополнения можно указать "page" и получать результат постранично, каждая страница имеет 10 элементов. В случае отсутвия или некоректного page будут возвращены все элементы


POST /shop/ — создание магазина; Данный метод получает json c объектом магазина, в ответ возвращает id созданной записи. 
Пример Json: {"name":"Гуливер", "city":"4", "street":"267", "house_number":"267", "time_open":"10:00", "time_close":"15:00"}


<h3>Примеры запросов</h3>
Все запросы можно выполнять через сайт https://mediasoft.mrdevil.ru/ (Единственное не получил сертификат, и нужно 1 раз "подтвердить" переход по https)<br>
https://mediasoft.mrdevil.ru/shop - Вернёт все магазины<br>
https://mediasoft.mrdevil.ru/shop?open=1&city=1 - Вернёт все открытые магазины которые находятся в городе 1<br>
https://mediasoft.mrdevil.ru/city?order=-name&page=1 - Вернёт все первые 10 городов в противоположном алфавитном порядке<br>
https://mediasoft.mrdevil.ru/city/Москва/street - Вернёт все улицы города Москвы<br>
https://mediasoft.mrdevil.ru/city/Казань/street?page=2 Вернёт ошибку, тк в данный момент города Казань в базе нет.<br>


<h3>Скрипт по добавлению города</h3>
В приложении shops имеется файл scp.py. Это консольный скрипт вызываемый консольной командой "python scp.py <Город>", далее выдаёт список из всех найденных городов, и вам нужно выбрать id нужного. Парсер работает с помощью сайта https://kladr-api.ru/ . При запросе города, а затем всех улиц этого города, идёт сравнение через parentGuid, а далее приходит осознание, что улицы далеко не все, поэтому скрипт не считаю полноценным, но в качестве теста вполне ничего.
