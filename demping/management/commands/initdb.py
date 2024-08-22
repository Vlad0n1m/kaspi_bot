import os
import time
import asyncio
from bs4 import BeautifulSoup
from requests import post
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from aiogram import Bot
from django.core.management.base import BaseCommand
from demping.models import Product
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')  # Replace 'myproject.settings' with your project settings

import django
django.setup()

# Load environment variables
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')
KASPI_LOGIN = os.getenv('KASPI_LOGIN')
KASPI_PASSWORD = os.getenv('KASPI_PASSWORD')

# Initialize Telegram bot
bot = Bot(token=BOT_TOKEN)

async def send_message(text):
    try:
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
    except Exception as e:
        print(e)

def login(log, pas):
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
    driver.find_element(By.XPATH, '//*[@id="user_email_field"]').send_keys(log + Keys.RETURN)
    driver.find_element(By.XPATH, '//*[@id="password_field"]').send_keys(pas + Keys.RETURN)
    time.sleep(3)
    driver.get("https://kaspi.kz/mc/#/")
    return driver

def get_all_products_from_kaspi(driver, page_qty):
    try:
        p_count = 0
        for i in range(1, page_qty + 1):
            driver.get(f'https://kaspi.kz/mc/#/products/active/{i}')
            time.sleep(4)
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            trs = soup.find('table', class_="table is-hoverable").find_all('tr')[1:-1]
            for tr in trs:
                name, my_articul = tr.find('p', class_="subtitle is-6").text.split('  ')[0], tr.find('p', class_="subtitle is-6").find('br').next_sibling.strip()
                url = f'https://kaspi.kz/mc/#/offer/{my_articul}'
                in_stock = tr.find('td', attrs={'data-label': 'Наличие в магазинах'}).text
                price = int(tr.find('td', attrs={'data-label': 'Цена, тенге'}).text.replace('\xa0', '').replace(' ', '').replace('₸', '').strip())
                if '_' not in my_articul:
                    driver.get(url)
                    time.sleep(3)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    link = 'https://kaspi.kz' + soup.find('div', class_='master-product-info-fields__value').find('a', href=True)['href']
                    articul = link.split('-')[-1].rstrip('/') + '_' + my_articul
                    print(articul)
                else: 
                    articul = my_articul
                existing_product = Product.objects.filter(name=name.strip(), admin_url=url.strip()).first()
                if existing_product:
                    existing_product.product_id = articul.strip()
                    existing_product.save()
                else:
                    product = Product(
                        name=name.strip(),
                        product_id=articul.strip(),
                        admin_url=url.strip(),
                        default_url=f'https://kaspi.kz/yml/offer-view/offers/{articul.strip().split("_")[0]}',
                        price=price,
                        recomendation_price=price,
                        min_price=price-100
                    )
                    product.save()
                p_count += 1
        return p_count
    except Exception as e:
        raise e

class Command(BaseCommand):
    help = 'Init or update products db from kaspi shop'

    def handle(self, *args, **kwargs):
        driver = login(KASPI_LOGIN, KASPI_PASSWORD)
        driver.get('https://kaspi.kz/mc/#/products/active/1')
        time.sleep(2)
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        pagination_links = soup.find('ul', class_='pagination-list').find_all('a', class_='pagination-link')
        page_qty = int(pagination_links[-1].text)
        count = get_all_products_from_kaspi(driver, page_qty)
        asyncio.run(send_message(f'⚠ БД Обновилась!\n\n⚠Мы нашли {count} товаров в админке!'))