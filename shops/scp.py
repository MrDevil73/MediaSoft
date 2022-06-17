import requests
import json
import sys
import sqlite3
from pathlib import Path


def Main():
    token = 'fkbbfnRiyy3TBAiBR729Nirk4SNzeA8H'
    url = "https://kladr-api.ru/api.php?"
    first_url = """https://kladr-api.ru/api.php?contentType=city&token=fkbbfnRiyy3TBAiBR729Nirk4SNzeA8H&query="""
    if len(sys.argv) > 1:

        list_cities = json.loads(requests.get(first_url + sys.argv[1]).content)
        if len(list_cities['result']) == 1:
            print("Город не найден, попробуйте ввести коректный город")
            return None

    list_cities2 = [(el['name'], el['type'], el['id'], el['guid'], el['zip']) for el in list_cities['result'][1:]]
    for i, el in enumerate(list_cities2):
        print(f"{i}. {el[1]} {el[0]} ZIP:{el[-1]}")

    print("\nВыберите номер города или нажмите Enter если хотите прервать процесс ")

    while True:
        chose = input()
        if chose == "":
            print('Процесс отменён.')
            return None
        elif chose.isdigit() and int(chose) > -1 and int(chose) < len(list_cities2):
            ch = list_cities2[int(chose)]
            break
        else:
            print("Попробуйте снова ")
    get_streets = json.loads(requests.get("https://kladr-api.ru/api.php?withParent=1&contentType=street&token=fkbbfnRiyy3TBAiBR729Nirk4SNzeA8H&regionId=" + ch[2]).content)
    list_only_streets = [(el['name'],) for el in get_streets['result'][1:] if el['parentGuid'] == ch[-2] and el['typeShort'] in ["пер", 'ул', 'проезд', 'ул', 'ш']]
    con = sqlite3.connect(f"{Path(__file__).parents[1]}/db.sqlite3")
    cur = con.cursor()
    cur.execute(f"""SELECT COUNT(*) FROM shops_city WHERE name='{ch[0]}'""")
    if cur.fetchone()[0] == 0:
        cur.execute(f"""INSERT INTO shops_city VALUES (NULL,'{ch[0]}')""")
        cur.execute(f"""SELECT id FROM shops_city WHERE name='{ch[0]}'""")
        _id = cur.fetchone()[0]
        cur.executemany(f"""INSERT INTO shops_street VALUES (NULL,?,{_id})""", list_only_streets)
        con.commit()

        print(f"Добавлен город {ch[0]}")
    else:
        print("Данный город уже есть.")
    con.close()


if __name__ == '__main__':
    Main()
