import os
import time
import requests
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()

class Kaspi:
    
    KASPI_LOGIN = os.getenv('KASPI_LOGIN')
    KASPI_PASSWORD = os.getenv('KASPI_PASSWORD')
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
    
    def __init__(self) -> None:
        pass
    
    def change_price(self, new_price: int, admin_url: str) -> dict:
        driver = self.get_driver()
        driver.get(f'https://kaspi.kz/mc/#/products/{admin_url.split('/')[-1]}')
        time.sleep(2)
        change_price_input = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div[2]/div/div[2]/div[2]/div/table/thead/tr[2]/th[2]/div/span/div[2]/input')
        if change_price_input:
            try:
                change_price_input.clear()
                time.sleep(1)
                change_price_input.send_keys(new_price)
                time.sleep(1)
            except Exception as err:
                driver.quit()
                driver.quit()
                driver.quit()
                return {'status': False, 'error': str(err)}

        else:
            driver.quit()
            driver.quit()
            driver.quit()
            return {'status': False, 'error': 'Поле для изменения цены не найдено.'}

        save_btn = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div[2]/div/div[2]/div[3]/button[1]')
        save_btn.click()
        time.sleep(2)
        driver.quit()
        driver.quit()
        driver.quit()
        return {'status': True}
    
    def get_product_info(self, api_url: str) -> dict:
        # if '_' in articul:
            # api_url = f'https://kaspi.kz/yml/offer-view/offers/{articul.split("_")[0]}'
        # else:
            # return {'status': False, 'error': f'"{articul}" - Артикул не корректен'}
        
        headers = {
            "Accept": "application/json, text/*",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Content-Type": "application/json; charset=UTF-8",
            "Cookie": "k_stat=c0391704-1dcd-4234-98dc-16fc1ba71479; ks.tg=94; kaspi.storefront.cookie.city=591010000; layout=d",
            "Host": "kaspi.kz",
            "Origin": "https://kaspi.kz",
            "Pragma": "no-cache",
            "Referer": "https://kaspi.kz/shop/p/vplab-mineral-no-vitaminnyi-kompleks-ultra-mens-90-tabletok-101166688/",
            "Sec-Ch-Ua": '"Chromium";v="124", "Brave";v="124", "Not-A.Brand";v="99"',
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "Windows",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Gpc": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "X-Ks-City": "591010000"
        }

        payload = {
            "cityId": "591010000",
            "id": "101166688",
            "installationId": "-1",
            "page": 0,
        }

        response = requests.post(api_url, json=payload, headers=headers)
        if response.status_code != 200:
            return {'status': False, 'error': f'{response.status_code} - Ответ сервера при получении инфо о предложениях'}
        offers = sorted(json.loads(response.text)['offers'], key=lambda x: x['price'])
        if offers:
            my_place = next((index for index, offer in enumerate(offers) if offer['merchantName'] == 'MaxNutrition'), None)
            if my_place is None:
                return {'status': '2', 'error': 'Товар снят с продажи'}
            my_place += 1
            info = {
                    "my_place": int(my_place), 
                    'my_price': int(offers[my_place - 1]['price']) if my_place else None,
                    'second_price': int(offers[1]['price']) if len(offers) >= 2 else None,
                    'top_price': int(offers[0]['price']),
                    'concurents': ','.join([item['merchantName'] for item in offers]), 
                }
        else: 
            return {'status': False, 'error': 'Сервер вернул пустой массив предложений'}
        
        return {'status': True, 'info': info}
    
    def get_driver(self) -> dict:
        chrome_options = Options()
        chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument('log-level=3')
        driver = webdriver.Chrome(options=chrome_options)
        driver.implicitly_wait(5)
        driver.get("https://kaspi.kz/mc/#/login")
        driver.find_element(By.XPATH, '//*[@id="9-label"]').click()
        driver.find_element(By.XPATH, '//*[@id="user_email_field"]').send_keys(self.KASPI_LOGIN + Keys.RETURN)
        driver.find_element(By.XPATH, '//*[@id="password_field"]').send_keys(self.KASPI_PASSWORD + Keys.RETURN)
        time.sleep(3)
        driver.get("https://kaspi.kz/mc/#/")
        return driver

# import os
# import time
# import requests
# import json
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.options import Options
# from dotenv import load_dotenv

# load_dotenv()

# class Kaspi:
    
#     KASPI_LOGIN = os.getenv('KASPI_LOGIN')
#     KASPI_PASSWORD = os.getenv('KASPI_PASSWORD')
#     TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
#     GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
#     DATABASE_URL = os.getenv('DB_URL')
    
#     def __init__(self) -> None:
#         pass
    
#     def change_price(self, new_price: int, admin_url: str) -> dict:
#         driver = self.get_driver()
#         driver.get(admin_url)
#         driver.refresh()
#         time.sleep(3)
#         driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div[2]/div/div[2]/div[2]/div/div[6]/div[2]/a').click()        
#         driver.refresh()
#         time.sleep(3)
#         try:
#             change_price_input = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div[2]/div/div[2]/div[2]/div/table/thead/tr[2]/th[2]/div/span/div[2]/input')
#         except Exception as e:
#             driver.refresh()
#             time.sleep(3)
#             try:
#                 # change_price_input = driver.find_element(By.CSS_SELECTOR, '#app > div:nth-child(2) > section > div.main-content > div > div.block > div.b-table > div > table > thead > tr.is-subheading > th:nth-child(2) > div > span > div:nth-child(2) > input')
#                 change_price_input = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div[2]/div/div[2]/div[2]/div/table/thead/tr[2]/th[2]/div/span/div[2]/input')
#             except:    
#                 return {'status': False, 'error': 'Поле для изменения цены не найдено.'}
#         if change_price_input:
#             try:
#                 change_price_input.clear()
#                 time.sleep(1)
#                 change_price_input.send_keys(new_price)
#                 time.sleep(1)
#             except Exception as err:
#                 driver.quit()
#                 return {'status': False, 'error': f'2 раза поле изменения цены не найдено {str(err)}'}

#         else:
#             driver.quit()
#             return {'status': False, 'error': 'Поле для изменения цены не найдено.'}

#         save_btn = driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div[2]/div/div[2]/div[3]/button[1]')
#         save_btn.click()
#         time.sleep(2)
#         driver.quit()
#         driver.quit()
#         driver.quit()
#         return {'status': True}
    
#     def get_product_info(self, articul: str) -> dict:
#         if '_' in str(articul):
#             api_url = f'https://kaspi.kz/yml/offer-view/offers/{articul.split("_")[0]}'
#         else:
#             return {'status': False, 'error': f'"{articul}" - Артикул не корректен'}
        
#         headers = {
#             "Accept": "application/json, text/*",
#             "Accept-Encoding": "gzip, deflate, br, zstd",
#             "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
#             "Cache-Control": "no-cache",
#             "Connection": "keep-alive",
#             "Content-Type": "application/json; charset=UTF-8",
#             "Cookie": "k_stat=c0391704-1dcd-4234-98dc-16fc1ba71479; ks.tg=94; kaspi.storefront.cookie.city=591010000; layout=d",
#             "Host": "kaspi.kz",
#             "Origin": "https://kaspi.kz",
#             "Pragma": "no-cache",
#             "Referer": "https://kaspi.kz/shop/p/vplab-mineral-no-vitaminnyi-kompleks-ultra-mens-90-tabletok-101166688/",
#             "Sec-Ch-Ua": '"Chromium";v="124", "Brave";v="124", "Not-A.Brand";v="99"',
#             "Sec-Ch-Ua-Mobile": "?0",
#             "Sec-Ch-Ua-Platform": "Windows",
#             "Sec-Fetch-Dest": "empty",
#             "Sec-Fetch-Mode": "cors",
#             "Sec-Fetch-Site": "same-origin",
#             "Sec-Gpc": "1",
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
#             "X-Ks-City": "591010000"
#         }

#         payload = {
#             "cityId": "591010000",
#             "id": "101166688",
#             "installationId": "-1",
#             "page": 0,
#         }

#         response = requests.post(api_url, json=payload, headers=headers)
#         if response.status_code != 200:
#             return {'status': False, 'error': f'{response.status_code} - Ответ сервера при получении инфо о предложениях'}
#         offers = sorted(json.loads(response.text)['offers'], key=lambda x: x['price'])
#         if offers:
#             my_place = next((index for index, offer in enumerate(offers) if offer['merchantName'] == 'MaxNutrition'), None)
#             if my_place is None:
#                 return {'status': False, 'error': 'Товар снят с продажи'}
#             my_place += 1
#             info = {
#                     "my_place": int(my_place), 
#                     'my_price': int(offers[my_place - 1]['price']) if my_place else None,
#                     'second_price': int(offers[1]['price']) if len(offers) >= 2 else None,
#                     'top_price': int(offers[0]['price']),
#                     'concurents': ','.join([item['merchantName'] for item in offers]), 
#                 }
#         else: 
#             return {'status': False, 'error': 'Сервер вернул пустой массив предложений'}
        
#         return {'status': True, 'info': info}
    
#     def get_driver(self) -> dict:
#         chrome_options = Options()
#         chrome_options.add_experimental_option("excludeSwitches", ['enable-automation'])
#         chrome_options.add_argument("--no-sandbox")
#         chrome_options.add_argument("--headless")
#         chrome_options.add_argument("--disable-dev-shm-usage")
#         chrome_options.add_argument("--window-size=1920,1080")
#         chrome_options.add_argument('log-level=3')
#         driver = webdriver.Chrome(options=chrome_options)
#         driver.implicitly_wait(5)
#         driver.get("https://kaspi.kz/mc/#/login")
#         driver.find_element(By.XPATH, '//*[@id="9-label"]').click()
#         driver.find_element(By.XPATH, '//*[@id="user_email_field"]').send_keys(self.KASPI_LOGIN + Keys.RETURN)
#         driver.find_element(By.XPATH, '//*[@id="password_field"]').send_keys(self.KASPI_PASSWORD + Keys.RETURN)
#         time.sleep(3)
#         driver.get("https://kaspi.kz/mc/#/")
#         return driver
