import os
import asyncio
from demping.management.commands.kaspi import Kaspi
from aiogram import Bot
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import time
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
import requests
import json
from selenium.webdriver.common.by import By
from demping.management.commands.whatsapp import send_whatsapp_message


load_dotenv()

KASPI_LOGIN = os.getenv('KASPI_LOGIN')
KASPI_PASSWORD = os.getenv('KASPI_PASSWORD')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROUP_CHAT_ID = os.getenv('ORDERS_CHAT_ID')
BUG_CHATID = os.getenv('BUG_CHATID')

bot = Bot(token=TELEGRAM_TOKEN)
executor = ThreadPoolExecutor()

message_queue = asyncio.Queue()

async def send_message(text, type='default'):
    if type == 'bug':
        await bot.send_message(chat_id=BUG_CHATID, text=text)
    else:
        try:
            await bot.send_message(chat_id=GROUP_CHAT_ID, text=text)
        except Exception as e:
            print(e)

def send_wapp_message(chat_id, message):
    url = "https://7103.api.greenapi.com/waInstance7103922786/sendMessage/cf1c9862947c4790bfa160ff2227bc0ead9eb9147b94471185"
    payload = {
        "chatId": chat_id + '@c.us',
        "message": message
    }
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.encoding = 'utf-8'  
    print(response.text)

async def process_orders():
    driver = None
    try:
        kaspi = Kaspi()
        driver = kaspi.get_driver()

        driver.get('https://kaspi.kz/mc/#/orders?status=NEW')
        time.sleep(3)
        html_content = driver.page_source.encode('utf-8', errors='ignore').decode('utf-8')
        soup = BeautifulSoup(html_content, 'html.parser')
        # Находим все div с классом 'row row-orderCode0'
        rows = soup.find_all('div', class_='row row-orderCode0')

        # Получаем href из всех найденных элементов
        urls = ['https://kaspi.kz/mc/' + row.find('a')['href'] for row in rows]
        print(urls)
        for url in urls:
            print(url)
            driver.get(url)
            driver.refresh()
            time.sleep(15)
            html_content = driver.page_source.encode('utf-8', errors='ignore').decode('utf-8')
            soup = BeautifulSoup(html_content, 'html.parser')
            order_number = soup.find('h1', class_='title is-5').get_text().split('№')[-1]

            table = soup.find('div', class_='table-wrapper').find('table')

            # Извлекаем все ссылки <a> из таблицы
            links = table.find_all('a')

            # Создаем нумерованный список текстов из ссылок
            numbered_list = [f"{index + 1}. {link.get_text(strip=True)}" for index, link in enumerate(links)]

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            driver.find_element(By.XPATH, '//*[@id="app"]/div[2]/section/div[2]/div/div[3]/div/div[8]/div[2]/button[1]').click()
            name = soup.find('span', class_='has-text-weight-medium has-text-black').text
            phone_links = soup.find_all('a', href=lambda href: href and href.startswith('tel:'))
            phone_numbers = [link.get_text(strip=True) for link in phone_links]
            columns = soup.find_all('div', class_='columns')
            city=soup.find('div', class_='pickup-point-wrapper').find('span').get_text()
            for column in columns:
                first_child = column.find('div', class_='is-flex')
                if first_child and 'Способ доставки' in first_child.get_text():
                    delivery_type = column.find('span').get_text()
                elif first_child and 'Планируемая дата доставки заказа' in first_child.get_text():
                    pref_date = column.find('span').get_text()
            wp_msg = send_whatsapp_message(phone_number=phone_numbers[0], client_name=name, products=",".join(numbered_list), pref_date=pref_date, order_number=order_number, delivery_type=delivery_type.strip(), city=city)
            await send_message(f'#заказ {order_number}\n\nНовый заказ!\n\n{name}\n\n{",".join(numbered_list)}\n\n{phone_numbers[0]}\n\nТип доставки - {delivery_type}\n\nПланируемая дата доставки - {pref_date}\n\nАдрес доставки - {city}\n\n{wp_msg}')
            time.sleep(5)
        driver.quit()
    except Exception as e:
        if driver:
            driver.quit()
        await send_message(f'#заказ {order_number}\n\nНовый заказ!\n\n{name}\n\n{",".join(numbered_list)}\n\n{phone_numbers[0]}\n\nТип доставки - {delivery_type}\n\nПланируемая дата доставки - {pref_date}\n\nАдрес доставки - {city}',type='bug')
        await send_message(str(e), type='bug')
        



class Command(BaseCommand):
    help = 'orders'
    def handle(self, *args, **kwargs):
        while 1:
            loop = asyncio.get_event_loop()
            async def accept_orders():
                await process_orders()
            loop.run_until_complete(accept_orders())