from multiprocessing import Pool

import numpy as np
from bs4 import BeautifulSoup
import requests


def rndwParsPage(url):
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

        obj["name"] = str(page.find("div", "b-header__mainTitle").text) + " " + str(page.find("div", "b-header__subtitle").text)
        obj["price"] = page.find_all("div", "s-productType__price")
        for i in range(len(obj["price"])):
            obj["price"][i] = obj["price"][i].contents
            if len(obj["price"][i]) > 1 and len(obj["price"][i]) != 3:
                obj["price"][i] = obj["price"][i][4].text
            elif len(obj["price"][i]) == 3:
                obj["price"][i] = obj["price"][i][0].text
            else:
                obj["price"][i] = 0
        obj["photo"] = page.find("img", "js-main-product-image s-productItem__imgMain").attrs["src"]
        info = page.find("dl", "dl").contents
        for i in range(len(info)):
            if "Верхние ноты" in info[i].text:
                obj["topNotes"] = info[i].text.replace("Верхние ноты", "")
            if "Средние ноты" in info[i].text:
                obj["middleNotes"] = info[i].text.replace("Средние ноты", "")
            if "Базовые ноты" in info[i].text:
                obj["baseNotes"] = info[i].text.replace("Базовые ноты", "")
            if "Пол" in info[i].text:
                obj["gender"] = info[i].text.replace("Пол", "")
        if obj["topNotes"] == "-" and obj["middleNotes"] == "-" and obj["baseNotes"] == "-":
            for i in range(len(info)):
                if "Ноты" in info[i].text:
                    obj["Ноты"] = info[i].text.replace("Ноты", "")

        info = page.find("ul", "product-types__list").contents
        while len(info[len(info) - 1].__getattribute__("attrs")) == 3:
            info.pop(len(info) - 1)
            obj["price"].pop(len(obj["price"]) - 1)
        str1 = info[0].text.split(" ")
        type = ''
        c = 0
        for el in str1:
            if "мл" in el:
                type = ' '.join(str1[:c])
                str1 = ""
            c += 1
        while type not in info[len(info) - 1].text:
            info.pop(len(info) - 1)
            obj["price"].pop(len(obj["price"]) - 1)
        for i in range(len(info)):
            info[i] = info[i].text.split("мл")[0].replace(type, "").split(" ")
            info[i] = info[i][len(info[i]) - 1].replace(" ", "").replace(",", ".")
            if "*" in info[i]:
                info[i] = float(info[i].split("*")[0]) * float(info[i].split("*")[1])
        for el in info:
            obj["size"].append(float(el))
        return obj
    except Exception as e:
        print(url)
        print(e)
        pass


def rndwParsCatalog(int):
    try:
        url = f"https://randewoo.ru/category/parfyumeriya?action=show&controller=categories&page={int}&slug=parfyumeriya"
        response = requests.get(url)
        page = BeautifulSoup(response.text, 'html.parser')
        list = page.find("ul", "products products--3").contents
        for el in list:
            if el.text == "":
                list.remove(el)
        for el in list:
            if "Aroma Box" in el.text:
                list.remove(el)
        for i in range(len(list)):
            list[i] = "https://randewoo.ru/" + str(list[i].__getattribute__("attrs")["data-url"])
        if len(list) < 60:
            list.append("https://randewoo.ru//product/marc-antoine-barrois-ganymede?source_category=6&preferred=343522")
        return list
    except Exception as e:
        print(int)
        print(e)
        pass


def rndwPars(count):
    numbers = range(1, count + 1)
    pages = []
    perfumes = []
    if __name__ == '__main__':
        p = Pool(processes=4)
        pages.extend(p.map(rndwParsCatalog, numbers))
        pages = np.array(pages).flatten()
        perfumes.extend(p.map(rndwParsPage, pages))
        perfumes = [np.array(perfumes).flatten()][0]
    return perfumes


abc = rndwPars(7)
print(abc)
