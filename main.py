from os import path
from bs4 import BeautifulSoup
import requests
import json
from unidecode import unidecode
import re
from dateutil import parser

def get_script(url):
    try:
        response = requests.get(url)
        if response.ok:
            rs = response.text
            return BeautifulSoup(rs, "lxml")
    except requests.exceptions.ConnectionError as exc:
        print(exc)
        return
    

def dating(date_string):
    match = re.search(r'\d+\s+de\s+\w+\s+de\s+\d{4}', date_string)
    if match:
        d = match.group(0).split()
        day = d[0]
        mounth = d[2]
        year = d[-1]
        mounth = {
            'enero': '01',
            'febrero': '02',
            'marzo': '03',
            'abril': '04',
            'mayo': '05',
            'junio': '06',
            'julio': '07',
            'agosto': '08',
            'septiembre': '09',
            'octubre': '10',
            'noviembre': '11',
            'diciembre': '12'
        }[mounth.lower()]
        date = f"{day}/{mounth}/{year}"
        return date 
    else:
        print("No se encontró una fecha en el string.")



def get_more_info(array, name):
    url = f"https://es.wikipedia.org/wiki/{name}"
    print(f"getting info of: {name}")
    content = get_script(url)
    VALID_DATA = ["nacimiento", "fallecimento", "apodo"]
    if content:
        try:
            table = content.find("table", class_="infobox")
            for item in table.find_all("tr"):
                key = BeautifulSoup(str(item.find("th", scope="row")), "lxml")
                value = BeautifulSoup(str(item.find("td", colspan="2")), "lxml")
                key = unidecode(key.get_text())
                value = unidecode(value.get_text())
                if key != "None" or value != "None":
                    if key.lower() in VALID_DATA:
                        if key.lower() == "nacimiento" or key.lower() == "fallecimento":
                            value = dating(value.replace("\n",""))
                        array[key.lower()] = value.replace("\n","")
        except:
            return


def transform_data(content):
    tbody = content.find("tbody")
    response = []
    for item in tbody.find_all("tr"):
        driver = {}
        names = item.find("a", class_="dark bold ArchiveLink")
        spans_names = names.find_all("span")
        driver["name"] = spans_names[0].get_text().title()
        driver["lastname"] = spans_names[1].get_text().title()
        driver["country"] = item.find("td", class_="dark semi-bold uppercase").get_text()
        driver["scudery"] = item.find("a", class_="grey semi-bold uppercase ArchiveLink").get_text()
        get_more_info(driver, f"{driver['name']} {driver['lastname']}")
        response.append(driver)
    return response


def create_file(filename, data):
    with open(filename, 'w', encoding='utf8') as fh:
        fh.write(json.dumps(data))


def init():
    year = 1950
    response = {}
    while year <= 2023:
        print(f"actually scrapping year {year}")
        url = f"https://www.formula1.com/en/results.html/{str(year)}/drivers.html"
        content = get_script(url)
        data = transform_data(content)
        response[year] = data
        year += 1
    create_file("subjects.json", response)
    print("the scrapping was completed")


init()
