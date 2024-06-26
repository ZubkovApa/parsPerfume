import time
import numpy as np

from multiprocessing import Pool
from bs4 import BeautifulSoup
from selenium import webdriver



# Обхождение проверки
def fixSecure(browser):
    c = 0
    while "будет выполнена проверка" in browser.page_source or "Выполняется проверка" in browser.page_source:
        time.sleep(5)
        c += 1
        if c == 10 or "не пройдена" in browser.page_source or "Не удается" in browser.page_source:
            browser.refresh()
            time.sleep(5)
    time.sleep(10)
    page = BeautifulSoup(browser.page_source, "html.parser")
    return page


def letuParsPage(url):
    try:
        # Создание класса парфюма, запуск страницы
        obj = { "name" : "-",
        "price" : [],
        "photo" : "-",
        "gender": "-",
        "topNotes" : "-",
        "middleNotes" : "-",
        "baseNotes" : "-",
        "size" : [] }
        browser = webdriver.Chrome()
        browser.get(url)
        time.sleep(5)
        page = fixSecure(browser)

        # Переключение на страницы с разным объёмом для сбора цен, занулении, если нет в наличии
        if "sku-view-table" in browser.page_source:
            allPageSourse = page.find("div", class_="sku-view-table").contents
            allPage = []
            for i in range(len(allPageSourse)):
                allPage.append("https://www.letu.ru" + allPageSourse[i].__getattribute__("attrs")["href"])
                browser.get(allPage[i])
                time.sleep(5)
                page = BeautifulSoup(browser.page_source, "html.parser")
                if "not-stock" in allPageSourse[i].__getattribute__("attrs")["class"][2]:
                    obj["price"].append(0)
                else:
                    if "product-detail-price__base-price product-detail-price__base-price--new-design" in browser.page_source:
                        obj["price"].append(int(page.find("span", class_="product-detail-price__base-price product-detail-price__base-price--new-design").text.replace(" ", "").replace("₽", "").replace("\n", "").replace("\xa0", "")))
                    else:
                        obj["price"].append(int(page.find("span", class_="product-detail-price__base-price product-detail-price__base-price--base").text.replace(" ", "").replace("₽", "").replace("\n", "").replace("\xa0", "")))

        # Поиск необходимых элементов на странице
        obj["name"] = page.find("h1", class_='product-detail-sku-header-left-block__title').text[5:][:-3]
        if "," in obj["name"]:
            obj["name"] = obj["name"].split(",")[0]
        obj["photo"] = page.find("img", class_="product-detail-media-carousel__horizontal-item-img").attrs['src']
        obj["photo"] = "https://www.letu.ru" + obj["photo"]
        info = page.find("div", class_="top-characteristics").contents
        for i in range(len(info) - 2):
            a = info[i].__getattribute__("contents")[0].text[9:][:-7]
            b = info[i].__getattribute__("contents")[2].text[9:][:-7].title()
            if a == "Верхние ноты":
                obj["topNotes"] = b
            elif a == "Ноты сердца":
                obj["middleNotes"] = b
            elif a == "Базовые ноты":
                obj["baseNotes"] = b
            elif a == "Пол":
                obj["gender"] = b

        if len(obj["price"]) == 0:
            obj["price"] = int(page.find("span", class_="product-detail-price__base-price product-detail-price__base-price--new-design").text.replace(" ", "").replace("₽", "").replace("\n", "").replace("\xa0", ""))

        if "product-detail-sku-volume__label" in browser.page_source:
            sizes = page.find_all("span", class_="product-detail-sku-volume__label")
            for el in sizes:
                obj["size"].append(int(el.next[:-3]))
        else:
            obj["size"] = int(page.find("div", class_="product-detail-sku-block__info").text[5:][:-6].split(" ")[-2])

        # Закрытие браузера, возврат эклемпляра класса парфюма
        browser.quit()
        return obj

    except Exception as e:
        print(url)
        print(e)
        pass

def letuParsCatalog(int):
    url = "https://www.letu.ru/browse/parfyumeriya/page-" + f"{int}"
    try:
        browser = webdriver.Chrome()
        browser.get(url)
        page = fixSecure(browser)
        list = page.find("div", class_="results-listing-content").contents
        for el in list:
            if el.text == "":
                list.remove(el)
        list.pop(0)
        for j in range(len(list)):
            list[j] = "https://www.letu.ru" + list[j].contents[2].__getattribute__("attrs")["href"]
        return list
    except Exception as e:
        print(url)
        print(e)
        pass


def letuPars(count):
    numbers = range(1, count + 1)
    pages = []
    perfumes = []
    if __name__ == '__main__':
        p = Pool(processes=4)
        pages.extend(p.map(letuParsCatalog, numbers))
        pages = np.array(pages).flatten()
        perfumes.extend(p.map(letuParsPage, pages))
        perfumes = [np.array(perfumes).flatten()][0]
    return perfumes


abc = letuPars(2)
print("ready")
