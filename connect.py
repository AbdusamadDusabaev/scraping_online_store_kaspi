import httplib2
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


password_sheet_id = "1V6P702lbcaBvpvbttfgiWaZKGeLXCOr6-8-ZKtsxlIs"
page_for_price = "Товары для анализа цен"
page_for_info = "Товары для анализа информации"
page_1 = "Цены"
page_2 = "Информация"
api_json = {
        "type": "service_account",
        "project_id": "kaspi-370623",
        "private_key_id": "bf154bf590215fac4ae65f9bc83f35e6e0e18ce1",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCqBxuGkvquSQGn\n615aVO1xKBCGxEirRVjW2xX3st6h4jHSL2P6pCkTuzWAKmVSHtlw7Sim7ckicUqc\n9B5Lq4exQEF691YZzPwN3v4JTj5L1mxmWI0gwne2pEx2vuj3oj/hm1UIum9oS8l3\nudLcj61p/yq5MUBh4pM9eWB4v4wzmj9cXipr+C7yQ5rcIr9cRyysCEuPR9ejjJAL\nSoDtDXhC7D9v7Y9M9jf8Yf7DLdl4X+80oIDDiBUqCA/uWEump8QqRhhEoHxzg3fj\nqasygPVLGes6MCuLtYZBplLVaIZd1pgOgFtwM3NE80+6rR+0kZZuZAXwvrf7Q0l5\ntfwdfSpTAgMBAAECggEADInHTlu4BQfY3un87xAJ4x56EC4Y+8RP4lGNTlL67EN9\nZWCy8JCQKjvTx1aZBSlwOHh3VyP8K+rgfoWEAb7YRp+/PxL5NEreSs7nEIbxZ29H\nAXRwknoKEPEPEHH7RQj1Hq0b5AUM4nXgQ/tzNhTu9qeR83koecTBveFIVhnYpr9k\n14cRO9ZCmsNMP5kTZlIOi3JB3uHWDXDi6Gk5ftgS83X3n3Z0huATm4gE65mdCs/y\nCXcGmpBq/+//e0MZeXUaK4ieuDm9S5/dQcteRr51mEVpjCmJKDiDkL7c5ITFn1wW\nziPDZNCk5UZ5BaDuRDMaYWrCJpJpFyhCHBhx7pjNwQKBgQDehB33ixG7O3s8CSVp\npkN9FKVy4CQgBXKpFE2KCjNCXEiWYw7mynF5WvYHYi/xHbUtwzyH+DujthHEaMme\ng6doAi0wERdIozHrLquKnyhjymohM1pAiJhPyfMfhBssCz/9MaEgKyBA2r0EPj7X\ne0BHiJdnJh3bAeiNZtKSQ9YjkwKBgQDDnQHtI3DgjO6UXZ++d3U8gv5zGJXCKWsL\nS8UhDCO8f5arUGdVMghOz9gXbchUKbRuSsMzhDyjA9cbs5x/f8swIWqZ9CQCT4vi\nxIPv46e5csFC9J41/yZe05mC0xKHpmUWAhtjG9ODv07iV5MF5/hLhiujSQ7d06ot\nUNyLH2KWQQKBgQC89ekU3G6UV3DRjNrOmzjYsX3Gzf0fjEDQwMMQJJVfF0s1Gq3+\n44/1hH9FyeX4lkfTsuZmeTD8V5NC/dGp4Rd6xc5l8T2am6u6koluULZV+ACkbR2J\ni/X8W/0wmFkS0ALpGwo/bSAYsyisv8dR6gKuPJqGJ+JWp4o6+kR7nUvuLQKBgB19\nVgUCCspPdMg5NRPpvmrY9LM1SZ5z0Adr7NQGmHyaX4SEIo/dcxMukk0157WIdAMM\nklD55opM0ekDMtylz2P6Ja//9k3C4DvXlGxdzbNPcYM+jXtmc8pn7ASk/W4lz6d5\nudc/IqwB80p8GVYSmoQIPhvnr64Rct5SCm2O1bYBAoGAM2D4AvIbqn6sVlSy3MuU\nPNFPvaEbi6y9elEX0EyvNDaXhftAvYtpMQ7OMLORWwlAvA8RoimMoGJy/COiIXpP\njcFNN6Inw8RTh3Nj8BqBHI/JgtAPeZsV7sC6BbwBSkOirr9IVbbd21Bqpb3Q2Y05\n6SBNuCztGUHYHRO3GGVgoas=\n-----END PRIVATE KEY-----\n",
        "client_email": "account@kaspi-370623.iam.gserviceaccount.com",
        "client_id": "114785817935838872604",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/account%40kaspi-370623.iam.gserviceaccount.com"
    }


def get_service_sacc():
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds_service = ServiceAccountCredentials.from_json_keyfile_dict(api_json, scopes=scopes).authorize(httplib2.Http())
    return build(serviceName="sheets", version="v4", http=creds_service)


def get_password():
    service = get_service_sacc()
    sheet = service.spreadsheets()
    response = sheet.values().get(spreadsheetId=password_sheet_id, range=f"password!B2").execute()
    result = response["values"][0][0]
    return result


def get_1(sheet_id):
    service = get_service_sacc()
    sheet = service.spreadsheets()
    response = sheet.values().get(spreadsheetId=sheet_id, range=f"{page_for_price}!A2:A100000").execute()

    result = list()
    for element in response["values"]:
        if element[0] not in result:
            result.append(element[0])
    return result


def get_2(sheet_id):
    service = get_service_sacc()
    sheet = service.spreadsheets()
    response = sheet.values().get(spreadsheetId=sheet_id, range=f"{page_for_info}!A2:A100000").execute()

    result = list()
    for element in response["values"]:
        if element[0] not in result:
            result.append(element[0])
    return result


def record_1(prices, index, city, price_mode, name, sheet_id):
    service = get_service_sacc()
    sheet = service.spreadsheets()
    if price_mode == 1:
        values = [[name, city]]
        body = {"values": values}
        sheet.values().update(spreadsheetId=sheet_id, range=f"{page_1}!F{index}",
                              valueInputOption="RAW", body=body).execute()

        price_3_hours = prices["За 3 часа"]
        price_today = prices["Сегодня"]
        price_tomorrow = prices["Завтра"]
        price_period = prices["Период"]
        values = [[price_3_hours, price_today, price_tomorrow, price_period]]
        body = {"values": values}
        sheet.values().update(spreadsheetId=sheet_id, range=f"{page_1}!I{index}",
                              valueInputOption="RAW", body=body).execute()
    else:
        values = [[name, city, prices]]
        body = {"values": values}
        sheet.values().update(spreadsheetId=sheet_id, range=f"{page_1}!F{index}",
                              valueInputOption="RAW", body=body).execute()


def record_2(item_info, index, name, sheet_id):
    service = get_service_sacc()
    sheet = service.spreadsheets()
    reviews = item_info["Отзывы"]
    ratings = item_info["Оценки"]
    rating = item_info["Рейтинг"]
    link = item_info["Ссылка"]
    product_id = item_info["Артикул"]
    sellers = item_info["Количество продавцов"]
    place_reviews = item_info["Место по отзывам"]
    place_sellers = item_info["Место по продавцам"]
    values = [[name, reviews, ratings, rating, link, product_id, sellers, place_reviews, place_sellers]]
    body = {"values": values}
    sheet.values().update(spreadsheetId=sheet_id, range=f"{page_2}!A{index}",
                          valueInputOption="RAW", body=body).execute()


if __name__ == "__main__":
    get_1(sheet_id="adlnvls")
