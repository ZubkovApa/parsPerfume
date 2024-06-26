import time
from multiprocessing import Pool

import numpy as np
from bs4 import BeautifulSoup
import requests


def duhiParsPage(url):
    try:
        # Создание класса парфюма, запуск страницы
        obj = {"name": "-",
               "price": [],
               "photo": "-",
               "gender": "-",
               "topNotes": "-",
               "middleNotes": "-",
               "baseNotes": "-",
               "size": []}

        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')

        type = page.find("div", "d-flex flex-column table-filter-description").text.split("(")[0].replace("\n", "")[1:][:-1]
        obj["name"] = page.find("h1", "isnarrow text-active-red mt-2 pt-1 pb-2 text-center text-xl-left").contents[1].text.replace("\t", "").replace("\n", "").replace(type, "")[2:]
        obj["size"] = page.find_all("td", "table_volume pl-2")
        obj["price"] = page.find_all("td", "table_price pl-0")
        for i in range(len(obj["size"])):
            obj["size"][i] = obj["size"][i].text.replace("мл", "").replace("Обьем", "").replace("\n", "").replace(" ", "")
            obj["price"][i] = float(obj["price"][i].text.replace("мл", "").replace("\n", "").replace(" ", "").split("р.")[0])
            if "+" in obj["size"][i]:
                obj["size"][i] = float(obj["size"][i].split("+")[0]) + float(obj["size"][i].split("+")[1])
            obj["size"][i] = float(obj["size"][i])

        obj["photo"] = "https://xn--d1ai6ai.xn--p1ai/" + page.find("img", "img-fluid multi").attrs["src"]
        obj["gender"] = page.find("a", "pr-1").contents[0].text

        info = page.find_all("div", "mb-1")
        for el in info:
            if "Верхние ноты" in el.text:
                obj["topNotes"] = el.contents[3].text.replace("\n", "").replace("\t", "")
            if "Ноты сердца" in el.text:
                obj["middleNotes"] = el.contents[3].text.replace("\n", "").replace("\t", "")
            if "Базовые ноты" in el.text:
                obj["baseNotes"] = el.contents[3].text.replace("\n", "").replace("\t", "")
        return obj
    except Exception as e:
        print(url)
        print(e)
        pass


def duhiParsCatalog():
    url = "https://xn--d1ai6ai.xn--p1ai/index.php?filter_search=1&section=6&category=all&price_from=0&price_to=99000&type[1]=1&type[2]=2&type[3]=3&type[4]=4&volume_from=0&volume_to=1000&new_pr=&sale=&vint_pr=&aviable_pr=&cmd=show_items"
    response = requests.get(url)
    page = BeautifulSoup(response.text, 'html.parser')
    list = []
    info = page.find("div", "row flex-wrap flex-justify-start").contents[:-3]
    for i in range(1, len(info), 2):
        info[i] = info[i].contents[1].contents[1].contents[3].attrs["href"]
        list.append("https:" + info[i])
    return list


def duhiPars():
    pages = duhiParsCatalog()
    perfumes = []
    if __name__ == '__main__':
        p = Pool(processes=4)
        perfumes.extend(p.map(duhiParsPage, pages))
        perfumes = [np.array(perfumes).flatten()][0]
    return perfumes

abc = duhiPars()
print(abc)
