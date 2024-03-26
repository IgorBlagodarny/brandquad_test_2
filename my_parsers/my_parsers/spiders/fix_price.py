import datetime
import json
import re
from copy import deepcopy
from typing import Iterable

import scrapy
from scrapy import Request
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy.http.response import Response
from w3lib.url import url_query_cleaner, add_or_replace_parameter, url_query_parameter

from .constants.fix_price import *


class FixPrice:
    def get_product_container(self):
        return {
            "timestamp": int(datetime.datetime.now().timestamp()),  # Дата и время сбора товара в формате timestamp.
            "RPC": "",  # Уникальный код товара.
            "url": "",  # Ссылка на страницу товара.
            "title": "",
            # Заголовок/название товара (! Если в карточке товара указан цвет или объем, но их нет в названии, необходимо добавить их в title в формате: "{Название}, {Цвет или Объем}").
            "marketing_tags": [],
            # Список маркетинговых тэгов, например: ['Популярный', 'Акция', 'Подарок']. Если тэг представлен в виде изображения собирать его не нужно.
            "brand": "",  # Бренд товара.
            "section": [],
            # Иерархия разделов, например: ['Игрушки', 'Развивающие и интерактивные игрушки', 'Интерактивные игрушки'].
            "price_data": {
                "current": 0.,  # Цена со скидкой, если скидки нет то = original.
                "original": 0.,  # Оригинальная цена.
                "sale_tag": ""
                # Если есть скидка на товар то необходимо вычислить процент скидки и записать формате: "Скидка {discount_percentage}%".
            },
            "stock": {
                "in_stock": False,  # Есть товар в наличии в магазине или нет.
                "count": 0
                # Если есть возможность получить информацию о количестве оставшегося товара в наличии, иначе 0.
            },
            "assets": {
                "main_image": "",  # Ссылка на основное изображение товара.
                "set_images": [],  # Список ссылок на все изображения товара.
                "view360": [],  # Список ссылок на изображения в формате 360.
                "video": []  # Список ссылок на видео/видеообложки товара.
            },
            "metadata": {
                "__description": "",
                # Также в metadata необходимо добавить все характеристики товара которые могут быть на странице.
                # Например: Артикул, Код товара, Цвет, Объем, Страна производитель и т.д.
                # Где KEY - наименование характеристики.
            },
            "variants": 0,
            # Кол-во вариантов у товара в карточке (За вариант считать только цвет или объем/масса. Размер у одежды или обуви варинтами не считаются).
        }

    def get_images(self, images_data):
        set_images = list(set([image['src'] for image in images_data]))
        main_image = set_images[0]
        return {
            'assets':
                {
                    'main_image': main_image,
                    'set_images': set_images,
                    "view360": [],
                    "video": []
                }
        }

    def get_stock(self, stock_count=0):
        return {
            'stock': {
                'count': stock_count,
                'in_stock': stock_count > 0
            }
        }

    def get_price_data(self, min_price, max_price, response):
        price_data = {"price_data":
            {
                "current": min(min_price, max_price),  # Цена со скидкой, если скидки нет то = original.
                "original": max(min_price, max_price),  # Оригинальная цена.
                "sale_tag": ""
                # Если есть скидка на товар то необходимо вычислить процент скидки и записать формате: "Скидка {discount_percentage}%".
            }
        }
        if price_data['price_data']["current"] != price_data['price_data']["original"]:
            discount_percentage = price_data['price_data']["current"] / price_data['price_data']["original"] * 100
            price_data['price_data']["sale_tag"] = f"Скидка {discount_percentage}%"

        # на сайте присутствует скидка для авторизованных пользователей
        # она хранится в nuxt script. достаём регуляркой при наличии
        if nuxt := response.xpath(SCRIPT_NUXT).get():
            card_price = re.search(r"unitType:b,specialPrice:\{price:\"(?P<price>\d+\.\d+)\"", nuxt)
            if card_price:
                price_data['price_data']['card_price'] = float(card_price.group('price'))

        return price_data

    def get_section(self, response):
        return {'section': response.xpath(PRODUCT_SECTIONS).getall()}

    def get_metadata(self, response):
        metadata = {"metadata": {"__description": ""}}
        description = response.xpath(PRODUCT_DESCRIPTION).get()
        metadata['metadata']['__description'] = description
        characteristics = [Selector(text=chr) for chr in response.xpath(PRODUCT_CHARACTERISTICS).getall()]
        for characteristic in characteristics:
            chr_name = characteristic.xpath(PRODUCT_CHARACTERISTIC_TITLE).get()
            chr_value = characteristic.xpath(PRODUCT_CHARACTERISTIC_VALUE).get()
            metadata['metadata'][chr_name] = chr_value

        return metadata

    def get_marketing_tags(self, response):
        marketing_tags = []
        #поиск скидки по карте FixPrice
        if nuxt := response.xpath(SCRIPT_NUXT).get():
            card_price = re.search(r"unitType:b,specialPrice:\{price:\"(?P<price>\d+\.\d+)\"", nuxt)
            if card_price:
                marketing_tags += ["Спец цена", "По карте «Fix Price»"]
        return {'marketing_tags': marketing_tags}


class FixPriceSpider(scrapy.Spider, FixPrice):
    name = "fix-price"
    start_urls = START_URLS
    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 30,
        'ITEM_PIPELINES': {
           "my_parsers.pipelines.ProductPipeline": 300,
        },
        "DOWNLOADER_MIDDLEWARES": {
           # "my_parsers.middlewares.ProxyMiddleware": 500,
        }
    }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def start_requests(self) -> Iterable[Request]:
        for url in self.start_urls:
            url_without_query = url_query_cleaner(url)
            category = re.search(r"/catalog/(?P<category>(\w+(-\w+)*)(/\w+(-\w+)*)*)",
                                 url_without_query)
            category_body = deepcopy(CATEGORY_BODY)
            category_body['category']= category.group("category")
            yield Request(CATEGORY_API_URL.format(slug=category_body['category'], page=1),
                          method='POST',
                          body=json.dumps(category_body),
                          headers=CATEGORY_HEADERS,
                          cookies=LOCATION_COOKIE,
                          cb_kwargs={'page': 1, 'body': category_body})

    def parse(self, response: HtmlResponse, **kwargs) -> Iterable[Request]:
        data = response.json()
        for product in data:
            product_data = {k: product.get(k, None) for k in ['id',
                                                              'title',
                                                              'url',
                                                              'images',
                                                              'minPrice',
                                                              'maxPrice',
                                                              'variantCount',
                                                              'brand',
                                                              'inStock']}

            yield Request(PRODUCT_FORMAT_URL.format(product_slug=product_data['url']),
                          callback=self.parse_product,
                          cookies=LOCATION_COOKIE,
                          cb_kwargs=product_data)

        if len(data) == 24:
            next_page = add_or_replace_parameter(response.url, 'page', kwargs.get('page') + 1)
            yield Request(next_page,
                          method='POST',
                          body=json.dumps(kwargs.get('body')),
                          headers=CATEGORY_HEADERS,
                          cookies=LOCATION_COOKIE,
                          cb_kwargs={'page': kwargs.get('page') + 1, 'body': kwargs.get('body')})

    def parse_product(self, response: Response, **kwargs) -> Iterable[dict]:
        result = self.get_product_container()
        result['RPC'] = kwargs.get('id')
        result['title'] = kwargs.get('title')
        result['url'] = PRODUCT_FORMAT_URL.format(product_slug=kwargs['url'])
        result['variants'] = kwargs.get('variantCount', 1)
        if kwargs.get('brand', {}):
            result['brand'] = kwargs.get('brand', {}).get("title", '')
        result.update(self.get_images(kwargs.get('images', [])))
        result.update(self.get_stock(kwargs.get('inStock', 0)))
        result.update(self.get_price_data(kwargs.get('minPrice', 0.), kwargs.get('maxPrice', 0.), response))
        result.update(self.get_metadata(response))
        result.update(self.get_section(response))
        result.update(self.get_marketing_tags(response))
        yield result
