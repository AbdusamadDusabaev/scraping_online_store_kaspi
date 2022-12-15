from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import time
import re
from connect import record_1, record_2, get_1, get_2, get_password


timeout = 30
domain = "https://kaspi.kz"
ua_iphone = " ".join(["Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X)",
                      "AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A356 Safari/604.1"])


def get_response(url, browser):
    error = 0
    try:
        browser.get(url=url)
    except TimeoutException:
        print("[ERROR] Не удалось получить ответ от сервера. Пробуем еще раз")
        error += 1
        if error == 5:
            return "error"
        else:
            return get_response(url=url, browser=browser)


def get_requests_response(url, headers):
    error = 0
    try:
        response = requests.get(url=url, headers=headers)
        bs_object = BeautifulSoup(response.content, "lxml")
        return bs_object
    except TimeoutException:
        print("[ERROR] Не удалось получить ответ от сервера. Пробуем еще раз")
        error += 1
        if error == 5:
            return "error"
        else:
            return get_requests_response(url=url, headers=headers)


def parsing_only_card(search_query, position):
    headers = {"user-agent": ua_iphone}
    url = f"https://kaspi.kz/shop/search/?text={search_query}"
    start_time = time.time()
    response = requests.get(url=url, headers=headers)
    stop_time = time.time()
    print("Время ответа сервера: ", stop_time - start_time)
    bs_object = BeautifulSoup(response.content, "lxml")
    items = bs_object.find_all(name="div", class_="item-card ddl_product")
    item = items[position]
    basic_info = item.find(name="a", class_="item-card__name ddl_product_link")
    price = item.find(name='span', class_="item-card__prices-price").text.strip()
    name = basic_info["title"]
    reviews_count = item.find(name="a", string=re.compile(r"\w*тзыво\w*")).text
    reviews = list()
    for symbol in reviews_count:
        if symbol.isdigit():
            reviews.append(symbol)
    reviews = "".join(reviews)
    link = domain + basic_info["href"]
    product_id = basic_info["data-product-id"]
    return [name, link, product_id, price, reviews]


def parsing_only_one_price(search_query, position):
    headers = {"user-agent": UserAgent().chrome}
    url = f"https://kaspi.kz/shop/search/?text={search_query}"
    start_time = time.time()
    response = requests.get(url=url, headers=headers)
    stop_time = time.time()
    print("[INFO] Время на получение запроса: ", stop_time - start_time)
    bs_object = BeautifulSoup(response.content, "lxml")
    items = bs_object.find_all(name="div", class_="item-card ddl_product")
    item = items[position]
    price = item.find(name='span', class_="item-card__prices-price").text.strip()
    return price


def parsing_1(search_query, position, city):  # Цены товара по вариантам доставки
    headers = {"user-agent": UserAgent().chrome}
    url = f"https://kaspi.kz/shop/search/?text={search_query}"
    request_time = time.time()
    bs_object = get_requests_response(url=url, headers=headers)
    if bs_object == "error":
        print("[ERROR] Не удалось получить ответ от сервера за 5 попыток")
        return "error"
    print("[INFO] Время на получение запроса: ", time.time() - request_time)

    item_links = bs_object.find_all(name="a", class_="item-card__image-wrapper ddl_product_link")[:2]
    if len(item_links) == 0:
        print(f"[INFO] На запрос {search_query} не найдено не одного товара")
        prices = {"За 3 часа": f"[INFO] На запрос {search_query} не найдено не одного товара",
                  "Сегодня": f"[INFO] На запрос {search_query} не найдено не одного товара",
                  "Завтра": f"[INFO] На запрос {search_query} не найдено не одного товара",
                  "Период": f"[INFO] На запрос {search_query} не найдено не одного товара"}
        return prices
    if position == 1:
        if len(item_links) > 1:
            item_link = [domain + item_link["href"] for item_link in item_links][position]
        else:
            print(f"[INFO] На запрос {search_query} есть только 1 позиция")
            prices = {"За 3 часа": f"[INFO] На запрос {search_query} есть только 1 позиция",
                      "Сегодня": f"[INFO] На запрос {search_query} есть только 1 позиция",
                      "Завтра": f"[INFO] На запрос {search_query} есть только 1 позиция",
                      "Период": f"[INFO] На запрос {search_query} есть только 1 позиция"}
            return prices
    else:
        item_link = [domain + item_link["href"] for item_link in item_links][position]
    if city != "Алматы":
        item_link = item_link.replace("c=750000000", "c=710000000")
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua_iphone}")
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(time_to_wait=timeout)
    wait_driver = WebDriverWait(browser, timeout)

    try:
        request_time = time.time()
        response = get_response(url=item_link, browser=browser)  # ссылка товара на Каспи
        if response == "error":
            print("[ERROR] Не удалось получить ответ от сервера за 5 попыток")
            return "error"
        print("[INFO] Время на получение запроса: ", time.time() - request_time)
        close_block_button = browser.find_element(By.CLASS_NAME, "current-location__background")
        browser.execute_script("arguments[0].click();", close_block_button)
        try:
            wait_driver.until(ec.visibility_of_element_located((By.CLASS_NAME, "seller-item__header")))
        except TimeoutException:
            return {"За 3 часа": "", "Сегодня": "", "Завтра": "", "Период": ""}
        sellers_invisible_object = bs_object.find(name="a", string=re.compile(r"Ещё \d* продав\w*"))

        java_script_time = time.time()

        if sellers_invisible_object is not None:
            more_sellers_button = browser.find_element(By.CLASS_NAME, "link-more")
            browser.execute_script("arguments[0].click();", more_sellers_button)

        time.sleep(5)
        print("[INFO] Время на загрузку JavaScript: ", time.time() - java_script_time)
        bs_object = BeautifulSoup(browser.page_source, "lxml")
        sellers = bs_object.find_all(name="div", class_="seller-item container")
        if len(sellers) > 10:
            sellers = sellers[:10]

        prices = {"За 3 часа": list(), "Сегодня": list(), "Завтра": list(), "Период": list()}
        for seller in sellers:
            price = seller.find(name='span', class_="seller-item__cost-price").text.strip()
            correct_price = list()
            for symbol in price:
                if symbol.isdigit():
                    correct_price.append(symbol)
            correct_price = int("".join(correct_price))
            delivery = seller.find(name="span", class_="sellers-table__delivery-date")
            if delivery is not None:
                delivery = delivery.text.strip()
                delivery_text = list()
                for symbol in delivery:
                    if symbol.isalpha():
                        delivery_text.append(symbol)
                delivery_text = "".join(delivery_text).lower()
                for delivery_mode in prices.keys():
                    if delivery_mode.lower() == delivery_text and delivery_mode != "Период":
                        prices[delivery_mode].append(correct_price)
                    elif delivery_mode == "Период":
                        prices[delivery_mode].append(correct_price)

        for delivery_mode in prices.keys():
            if len(prices[delivery_mode]) > 0:
                prices[delivery_mode] = min(prices[delivery_mode])
            else:
                prices[delivery_mode] = "-"
        return prices
    finally:
        browser.close()
        browser.quit()


def sub_parsing_3(browser, url, wait_driver):
    request_time = time.time()
    response = get_response(url=url, browser=browser)
    if response == "error":
        print("[ERROR] Не удалось получить ответ от сервера за 5 попыток")
        return "error"
    print("[INFO] Время на получение запроса: ", time.time() - request_time)
    response = browser.page_source
    bs_object = BeautifulSoup(response, "lxml")
    item_info = bs_object.find(name="script", string=re.compile(r"window.digitalData.produc\w*")).text.strip()
    item_info = eval(
        item_info.replace("window.digitalData.product=", "").replace("false", "False").replace("true", "True")[:-1])
    reviews_count = item_info["reviewCount"]  # отзывы товара на Каспи
    close_block = bs_object.find(name=True, class_="current-location__background")
    if close_block is not None:
        close_block_button = browser.find_element(By.CLASS_NAME, "current-location__background")
        browser.execute_script("arguments[0].click();", close_block_button)

    start = time.time()
    try:
        wait_driver.until(ec.visibility_of_element_located((By.CLASS_NAME, "seller-item__header")))
    except TimeoutException:
        print("", end="")
    stop = time.time()
    print(f"[INFO] На подгрузку JavaScript ушло {stop - start} секунд")

    response = browser.page_source
    bs_object = BeautifulSoup(response, "lxml")
    sellers_visible = bs_object.find_all(name="div", class_="seller-item container")
    sellers_visible_count = len(sellers_visible)
    sellers_invisible_object = bs_object.find(name="a", string=re.compile(r"Ещё \d* продав\w*"))

    if sellers_invisible_object is not None:
        sellers_invisible = sellers_invisible_object.text.strip()
        sellers_invisible_count = list()
        for symbol in sellers_invisible:
            if symbol.isdigit():
                sellers_invisible_count.append(symbol)
        sellers_invisible_count = int("".join(sellers_invisible_count))
    else:
        sellers_invisible_count = 0
    sellers_count = sellers_invisible_count + sellers_visible_count  # количество продавцов
    result = {"Отзывы": reviews_count, "Количество продавцов": sellers_count}
    return result


def parsing_3(browser, category_url, reviews_item, sellers_item, wait_driver):
    result_sellers_count = [sellers_item]
    result_reviews_count = [reviews_item]
    for page in range(1, 3):
        headers = {"user-agent": UserAgent().chrome}
        start = time.time()
        bs_object = get_requests_response(url=f"{category_url}&page={page}", headers=headers)
        print("[INFO] Время на получение запроса: ", time.time() - start)
        item_links = bs_object.find_all(name="a", class_="item-card__image-wrapper ddl_product_link")
        for item_link in item_links:
            url = domain + item_link["href"]
            print(f"[INFO] Собираем данные товара по ссылке {url}")
            sub_result = sub_parsing_3(browser=browser, url=url, wait_driver=wait_driver)
            while sub_result == "error":
                sub_result = sub_parsing_3(browser=browser, url=url, wait_driver=wait_driver)
            reviews_count = sub_result["Отзывы"]
            sellers_count = sub_result["Количество продавцов"]
            result_reviews_count.append(reviews_count)
            result_sellers_count.append(sellers_count)
    result_reviews_count = sorted(result_reviews_count, reverse=True)
    result_sellers_count = sorted(result_sellers_count, reverse=True)
    reviews_index = result_reviews_count.index(reviews_item) + 1
    sellers_index = result_sellers_count.index(sellers_item) + 1
    result = {"По отзывам": reviews_index, "По продавцам": sellers_index}
    return result


def parsing_2(search_query, position):  # Ссылка на товар, название товара, артикул, рейтинг, отзывы, оценки
    headers = {"user-agent": UserAgent().chrome}
    url = f"https://kaspi.kz/shop/search/?text={search_query}"
    request_time = time.time()
    bs_object = get_requests_response(url=url, headers=headers)
    if bs_object == "error":
        print("[ERROR] Не удалось получить ответ от сервера за 5 попыток")
        return "error"
    print(f"[INFO] Время на получение запроса {time.time() - request_time}")
    item_links = bs_object.find_all(name="a", class_="item-card__image-wrapper ddl_product_link")[:2]
    if len(item_links) == 0:
        print(f"[INFO] На запрос {search_query} не найдено не одного товара")
        result = {"Отзывы": "",
                  "Оценки": "",
                  "Рейтинг": "",
                  "Ссылка": "",
                  "Артикул": "",
                  "Количество продавцов": ""}
        return result
    if position == 1:
        if len(item_links) > 1:
            item_link = [domain + item_link["href"] for item_link in item_links][position]
        else:
            print(f"[INFO] На запрос {search_query} есть только 1 позиция")
            result = {"Отзывы": "",
                      "Оценки": "",
                      "Рейтинг": "",
                      "Ссылка": "",
                      "Артикул": "",
                      "Количество продавцов": ""}
            return result
    else:
        item_link = [domain + item_link["href"] for item_link in item_links][position]
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua_iphone}")
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(time_to_wait=timeout)
    wait_driver = WebDriverWait(browser, timeout)

    try:
        request_time = time.time()
        response = get_response(url=item_link, browser=browser)  # ссылка товара на Каспи
        if response == "error":
            print("[ERROR] Не удалось получить ответ от сервера за 5 попыток")
            return "error"
        print("[INFO] Время на получение запроса: ", time.time() - request_time)
        response = browser.page_source
        bs_object = BeautifulSoup(response, "lxml")
        item_info = bs_object.find(name="script", string=re.compile(r"window.digitalData.produc\w*")).text.strip()
        item_info = eval(
            item_info.replace("window.digitalData.product=", "").replace("false", "False").replace("true", "True")[:-1])
        product_id = item_info["id"]  # артикул товара на Каспи
        rating = item_info["rating"]  # рейтинг товара на Каспи
        reviews_count = item_info["reviewCount"]  # отзывы товара на Каспи
        close_block_button = browser.find_element(By.CLASS_NAME, "current-location__background")
        browser.execute_script("arguments[0].click();", close_block_button)
        if rating != 0:
            java_script_time = time.time()
            wait_driver.until(ec.visibility_of_element_located((By.CLASS_NAME, 'reviews__stats-display-info')))
            print("[INFO] Время на подгрузку JavaScript: ", time.time() - java_script_time)
            response = browser.page_source

        bs_object = BeautifulSoup(response, "lxml")
        rating_info = bs_object.find(name="div", class_='reviews__stats-display-info')
        if rating_info is not None:
            rating_info = rating_info.text.strip()
            rating_count = int(rating_info.split("\n")[0])  # оценки
        else:
            rating_count = 0  # оценки

        start = time.time()
        try:
            wait_driver.until(ec.visibility_of_element_located((By.CLASS_NAME, "seller-item__header")))
        except TimeoutException:
            print("", end="")
        stop = time.time()
        print(f"[INFO] На подгрузку JavaScript ушло {stop - start} секунд")

        response = browser.page_source
        bs_object = BeautifulSoup(response, "lxml")
        sellers_visible = bs_object.find_all(name="div", class_="seller-item container")
        sellers_visible_count = len(sellers_visible)
        sellers_invisible_object = bs_object.find(name="a", string=re.compile(r"Ещё \d* продав\w*"))

        if sellers_invisible_object is not None:
            sellers_invisible = sellers_invisible_object.text.strip()
            sellers_invisible_count = list()
            for symbol in sellers_invisible:
                if symbol.isdigit():
                    sellers_invisible_count.append(symbol)
            sellers_invisible_count = int("".join(sellers_invisible_count))
        else:
            sellers_invisible_count = 0
        sellers_count = sellers_invisible_count + sellers_visible_count  # количество продавцов
        category_url = bs_object.find_all(name="a", class_="chevrone-listing__item")[1]["href"]
        places = parsing_3(browser=browser, category_url=category_url,
                           reviews_item=reviews_count, sellers_item=sellers_count, wait_driver=wait_driver)
        place_reviews = places["По отзывам"]
        place_sellers = places["По продавцам"]
        result = {"Отзывы": reviews_count, "Оценки": rating_count, "Рейтинг": rating, "Ссылка": item_link,
                  "Артикул": product_id, "Количество продавцов": sellers_count, "Место по отзывам": place_reviews,
                  "Место по продавцам": place_sellers}
        return result
    finally:
        browser.close()
        browser.quit()


def parsing(search_query, position, city):
    headers = {"user-agent": UserAgent().chrome}
    url = f"https://kaspi.kz/shop/search/?text={search_query}"
    request_time = time.time()
    response = requests.get(url=url, headers=headers)
    print("Время на получение 1 запроса: ", time.time() - request_time)
    bs_object = BeautifulSoup(response.content, "lxml")
    item_links = bs_object.find_all(name="a", class_="item-card__image-wrapper ddl_product_link")[:2]
    item_link = [domain + item_link["href"] for item_link in item_links][position]
    if city != "Алматы":
        item_link = item_link.replace("c=750000000", "c=710000000")
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={ua_iphone}")
    options.add_argument("--headless")
    browser = webdriver.Chrome(options=options)
    browser.set_page_load_timeout(time_to_wait=timeout)
    wait_driver = WebDriverWait(browser, timeout)

    try:
        request_time = time.time()
        browser.get(item_link)  # ссылка товара на Каспи
        time.sleep(3)
        print("Время на получение второго запроса: ", time.time() - request_time)
        response = browser.page_source
        bs_object = BeautifulSoup(response, "lxml")
        item_info = bs_object.find(name="script", string=re.compile(r"window.digitalData.produc\w*")).text.strip()
        item_info = eval(
            item_info.replace("window.digitalData.product=", "").replace("false", "False").replace("true", "True")[:-1])
        product_id = item_info["id"]  # артикул товара на Каспи
        kaspi_name = item_info["name"]  # название товара на Каспи
        rating = item_info["rating"]  # рейтинг товара на Каспи
        reviews_count = item_info["reviewCount"]  # отзывы товара на Каспи
        close_block_button = browser.find_element(By.CLASS_NAME, "current-location__background")
        browser.execute_script("arguments[0].click();", close_block_button)
        if rating != 0:
            java_script_time = time.time()
            wait_driver.until(ec.visibility_of_element_located((By.CLASS_NAME, 'reviews__stats-display-info')))
            print("Время на подгрузку JavaScript: ", time.time() - java_script_time)
            response = browser.page_source

        bs_object = BeautifulSoup(response, "lxml")
        rating_info = bs_object.find(name="div", class_='reviews__stats-display-info')
        if rating_info is not None:
            rating_info = rating_info.text.strip()
            rating_count = int(rating_info.split("\n")[0])
        else:
            rating_count = ""
        sellers_visible = bs_object.find_all(name="div", class_="seller-item container")
        sellers_visible_count = len(sellers_visible)
        sellers_invisible_object = bs_object.find(name="a", string=re.compile(r"Ещё \d* продав\w*"))

        if sellers_invisible_object is not None:
            sellers_invisible = sellers_invisible_object.text.strip()
            sellers_invisible_count = list()
            for symbol in sellers_invisible:
                if symbol.isdigit():
                    sellers_invisible_count.append(symbol)
            sellers_invisible_count = int("".join(sellers_invisible_count))
        else:
            sellers_invisible_count = 0
        sellers_count = sellers_invisible_count + sellers_visible_count

        java_script_time = time.time()

        if sellers_invisible_object is not None:
            more_sellers_button = browser.find_element(By.CLASS_NAME, "link-more")
            browser.execute_script("arguments[0].click();", more_sellers_button)

        time.sleep(5)
        print("Время на загрузку JavaScript: ", time.time() - java_script_time)
        bs_object = BeautifulSoup(browser.page_source, "lxml")
        sellers = bs_object.find_all(name="div", class_="seller-item container")
        if len(sellers) > 10:
            sellers = sellers[:10]

        prices = {"За 3 часа": list(), "Сегодня": list(), "Завтра": list(), "Период": list()}
        for seller in sellers:
            price = seller.find(name='span', class_="seller-item__cost-price").text.strip()
            correct_price = list()
            for symbol in price:
                if symbol.isdigit():
                    correct_price.append(symbol)
            correct_price = int("".join(correct_price))
            delivery = seller.find(name="span", class_="sellers-table__delivery-date")
            if delivery is not None:
                delivery = delivery.text.strip()
                delivery_text = list()
                for symbol in delivery:
                    if symbol.isalpha():
                        delivery_text.append(symbol)
                delivery_text = "".join(delivery_text).lower()
                for delivery_mode in prices.keys():
                    if delivery_mode.lower() == delivery_text and delivery_mode != "Период":
                        prices[delivery_mode].append(correct_price)
                    elif delivery_mode == "Период":
                        prices[delivery_mode].append(correct_price)

        for delivery_mode in prices.keys():
            if len(prices[delivery_mode]) > 0:
                prices[delivery_mode] = min(prices[delivery_mode])
            else:
                prices[delivery_mode] = str()
        sub_result = {"kaspi_name": kaspi_name, "url": item_link, "product_id": product_id, "city": city,
                      "price_3_hours": prices["За 3 часа"], "price_today": prices["Сегодня"],
                      "price_tomorrow": prices["Завтра"], "price_period": prices["Период"],
                      "sellers_count": sellers_count, "rating_count": rating_count, "reviews_count": reviews_count,
                      "rating": rating}
        return sub_result
    except Exception as ex:
        print(f"При парсинге товара {search_query} произошла ошибка {ex}")
    finally:
        browser.close()
        browser.quit()


def task1(price_mode, products, position, region, sheet_id):
    if region == 1:
        cities = ["Алматы", "Регионы"]
        index = 2
    else:
        cities = ["Алматы"]
        index = 1
    print("[INFO] Программа запущена")
    print("=" * 100)
    print("=" * 100)
    for product in products:
        for city in cities:
            if region == 1:
                index += 1
            else:
                index += 2
            print(f"[INFO] Собираем цены о товаре {product} по городу {city}")
            start_item_time = time.time()
            if price_mode == 1:
                result = parsing_1(search_query=product, position=position, city=city)
                while result == "error":
                    result = parsing_1(search_query=product, position=position, city=city)
            else:
                result = parsing_only_one_price(search_query=product, position=position)
            record_1(prices=result, city=city, index=index, price_mode=price_mode, name=product, sheet_id=sheet_id)
            stop_item_time = time.time()
            print(f"[INFO] На обработку товара {product} ушло {stop_item_time - start_item_time} секунд")
            print("=" * 100)
            print()


def task2(products, position, sheet_id):
    index = 2
    print("[INFO] Программа запущена")
    print("=" * 100)
    print("=" * 100)
    for product in products:
        index += 1
        print(f"[INFO] Собираем информацию о товаре {product}")
        start_item_time = time.time()
        result = parsing_2(search_query=product, position=position)
        while result == "error":
            result = parsing_2(search_query=product, position=position)
        record_2(item_info=result, index=index, name=product, sheet_id=sheet_id)
        stop_item_time = time.time()
        print(f"[INFO] На обработку товара {product} ушло {stop_item_time - start_item_time} секунд")
        print("=" * 100)
        print()


def main(sheet_id):
    task = input("[INPUT] Выберете этап парсинга (1 - сбор цены или 2 - сбор информации): ")
    if task != "1" and task != "2":
        print(f"[ERROR] Вы ввели неверные данные. Попробуйте еще раз")
        return False
    position = int(input("[INPUT] Выберете, по какой позиции парсим (1 или 2): "))
    if position != 1 and position != 2:
        print(f"[ERROR] Вы ввели неверные данные. Попробуйте еще раз")
        return False
    position -= 1
    if task == "1":
        region = int(input("[INPUT] Выберете включение регионов (1 - включить, 2 - только город Алматы): "))
        if region != 1 and region != 2:
            print(f"[ERROR] Вы ввели неверные данные. Попробуйте еще раз")
            return False
        price_mode = int(input("[INPUT] Выберете сколько цен парсим (1 - все цены, 2 - только одну): "))
        if price_mode != 1 and price_mode != 2:
            print("[ERROR] Вы ввели неверные данные. Попробуйте еще раз")
            return False
        start = time.time()
        products = get_1(sheet_id=sheet_id)
        task1(products=products, position=position, region=region, price_mode=price_mode, sheet_id=sheet_id)
        print(f"[INFO] Общее время парсинга {len(products)} товаров: {time.time() - start}")
        return True
    elif task == "2":
        start = time.time()
        products = get_2(sheet_id=sheet_id)
        task2(products=products, position=position, sheet_id=sheet_id)
        print(f"[INFO] Общее время парсинга {len(products)} товаров: {time.time() - start}")
        return True


def run_program():
    try:
        while True:
            user_password = input("[INPUT] Введите пароль: ")
            if user_password == get_password():
                user_sheet_id = input("[INPUT] Введите ID Таблицы: ")
                main_result = main(sheet_id=user_sheet_id)
                if main_result:
                    break
            else:
                print("[ERROR] Введен неверный пароль. Попробуйте еще раз")
    except Exception as exc:
        print("[ERROR] Произошла ошибка. Убедитесь, что все данные были введены верно")
        print(f"[ERROR] Error: {exc}")

    while True:
        print("+" * 100)
        print("+" * 100)
        again = input("[INFO] Программа завершена. Введите quit - чтобы выйти, run - чтобы запустить парсер еще раз: ")
        if again == "quit":
            return False
        elif again == "run":
            return True
        else:
            print("[ERROR] Вы ввели неверную команду. Попробуйте еще раз")


if __name__ == "__main__":
    while True:
        run_again = run_program()
        if not run_again:
            break
