import os
import time
import asyncio
from django.core.management.base import BaseCommand
from aiogram import Bot
from django.db import models
from django.utils.decorators import sync_and_async_middleware
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger('django')

BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')

bot = Bot(token=BOT_TOKEN)

# Ensure you have the right imports for your models and Kaspi class
from demping.models import Product
from demping.management.commands.kaspi import Kaspi

async def change_price(i, kaspi, product, info, new_price, reason):
    if new_price == -333:
        tag = product.name.replace(' ', "_")
        await bot.send_message(chat_id=GROUP_CHAT_ID, text=f"#{i}\n\n#{tag}\n\n⚒: {reason}")
    else:
        if new_price != info['my_price']:
            change_result = kaspi.change_price(new_price=new_price, admin_url=product.admin_url)
            tag = product.name.replace(' ', "_")
            if change_result['status']:
                # Update product info using sync_to_async
                await sync_to_async(product.save)()
                await bot.send_message(chat_id=GROUP_CHAT_ID, text=f"#{i}\n\n#{tag}\n\n⚒: {reason}\n\n✅ Цена на товар {product.name} изменена с {info['my_price']} на {new_price}.")
            else:
                await bot.send_message(chat_id=GROUP_CHAT_ID, text=f"#{i}\n\n#{tag}\n\n⚒: {reason}\n\n❌ Не удалось изменить цену на товаре {product.name}: {change_result['error']}")

async def demp2(i, product, kaspi):
    await bot.send_message(chat_id=GROUP_CHAT_ID, text='STARTED')
    product_info = kaspi.get_product_info(product.default_url)
    
    if product_info['status'] == '2':
        pass
    elif product_info['status']:
        info = product_info['info']
        if info['my_place'] != 1 and product.recomendation_price >= info['top_price'] - 1 >= product.min_price:
            reason = "Новая цена товара будет меньше чем цена у топ-1 и при этом наша новая цена не меньше минимальной и не больше рекомендованной"
            new_price = info['top_price'] - 1
            await change_price(i, kaspi, product, info, new_price, reason)
        elif info['my_place'] != 1 and product.recomendation_price <= info['top_price'] - 1:
            reason = "Новая цена будет больше чем рекомендованная, поэтому ставим на рекомендованную."
            new_price = int(product.recomendation_price)
            await change_price(i, kaspi, product, info, new_price, reason)
        elif info['my_place'] != 1 and product.min_price >= info['top_price'] - 1:
            reason = "Новая цена будет меньше минимальной, надо подождать пока конкуренты вернут цену обратно к рекомендованной, мы тоже поставим сейчас рекомендованную"
            new_price = int(product.recomendation_price)
            await change_price(i, kaspi, product, info, new_price, reason)
        elif info['second_price'] is None:
            reason = 'Нет конкурентов, ставлю рекомендованную цену'
            new_price = int(product.recomendation_price)
            await change_price(i, kaspi, product, info, new_price, reason)
        elif info['my_place'] == 1 and info['second_price'] - info['my_price'] > 1:
            delta = info['second_price'] - info['my_price']
            new_price = int(info['second_price'] - 1)
            reason = f'Мы топ 1, цена топ 2 отошла от нас на {delta} тг, надо вернуть прибыль'
            if new_price < product.min_price:
                new_price = product.min_price
                reason += '\n\nновая цена упирается в минималку - поставим минималку'
            elif new_price > product.recomendation_price:
                new_price = product.recomendation_price
                reason += '\n\nновая цена упирается в рекомендованную - поставим рекомендованную'
            await change_price(i, kaspi, product, info, new_price, reason)
        elif info['my_price'] > product.recomendation_price:
            reason = "На каспи стояла цена больше чем рекомендованная.. надо поставить рекомендованную тогда."
            new_price = int(product.recomendation_price)
            await change_price(i, kaspi, product, info, new_price, reason)
        elif info['my_price'] < product.min_price:
            reason = "На каспи стояла цена меньше чем минимальная.. надо поставить рекомендованную тогда."
            new_price = int(product.recomendation_price)
            await change_price(i, kaspi, product, info, new_price, reason)
    else:
        reason = product_info['error']
        new_price = -333
        await change_price(i, kaspi, product, [], new_price, reason)

class Command(BaseCommand):
    help = 'Updates product prices'

    def handle(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        logger.info('Starting update_prices command.')
        kaspi_instance = Kaspi()

        # Retrieve products based on their mode
        products = Product.objects.filter(mode=True)
        print(len(products))
        
        async def update_product_prices():
            i=0
            for product in products:
                await demp2(i, product, kaspi_instance)
                await asyncio.sleep(1)
                i += 1
        
        start_time = time.time()
        loop.run_until_complete(update_product_prices())
        elapsed_time = time.time() - start_time
        loop.run_until_complete(bot.send_message(chat_id=GROUP_CHAT_ID, text=f"Время выполнения: {elapsed_time:.2f} секунд."))

        loop.close()