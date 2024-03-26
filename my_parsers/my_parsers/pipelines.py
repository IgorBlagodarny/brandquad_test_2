# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

from .spiders.fix_price import FixPrice


class ProductPipeline:
    product = FixPrice()

    def process_item(self, item, spider):
        self.check_timestamp(item)
        self.check_RPC(item)
        self.check_url(item)
        self.check_title(item)
        self.check_marketing_tags(item)
        self.check_brand(item)
        self.check_section(item)
        self.check_price_data(item)
        self.check_stock(item)
        self.check_assets(item)
        self.check_metadata(item)
        self.check_variants(item)
        return item


    def check_timestamp(self, item):
        if type(item['timestamp']) != int:
            item['timestamp'] = 0

    def check_RPC(self, item):
        if type(item['RPC']) != str:
            try:
                item['RPC'] = str(item['RPC'])
            except:
                raise DropItem("Bad RPC")

    def check_url(self, item):
        if type(item['url']) != str:
            try:
                item['url'] = str(item['url'])
            except:
                raise DropItem("Bad URL")

    def check_title(self, item):
        if type(item['title']) != str:
            try:
                item['title'] = str(item['title'])
            except:
                raise DropItem("Bad Title")

    def check_marketing_tags(self, item):
        if type(item['marketing_tags']) != list:
            item['marketing_tags'] = []

    def check_brand(self, item):
        if type(item['brand']) != str:
            try:
                item['brand'] = str(item['brand'])
            except:
                raise DropItem("Bad Brand")

    def check_section(self, item):
        if type(item['section']) != list:
            item['section'] = []

    def check_price_data(self, item):
        if type(item['price_data']) != dict:
            item['marketing_tags'] = {}
        if isinstance(item['price_data']['current'], (int, float)):
            item['price_data']['current'] = .0
        if isinstance(item['price_data']['original'], (int, float)):
            item['price_data']['original'] = .0
        if type(item['price_data']['sale_tag']) != str:
            item['price_data']['sale_tag'] = ''

    def check_stock(self, item):
        if type(item['stock']) != dict:
            item['stock'] = {}
        if type(item['stock']['in_stock']) != bool:
            item['stock']['in_stock'] = False
        if type(item['stock']['count']) != int :
            item['stock']['count'] = 0

    def check_assets(self, item):
        if type(item['assets']) != dict:
            item['assets'] = {}
        if type(item['assets']['main_image']) != str:
            item['assets']['main_image'] = ''
        if type(item['assets']['set_images']) != list:
            item['assets']['original'] = []
        if type(item['assets']['view360']) != list:
            item['assets']['view360'] = []
        if type(item['assets']['video']) != list:
            item['assets']['video'] = []

    def check_metadata(self, item):
        if type(item['metadata']) != dict:
            item['metadata'] = {}
        else:
            delete_keys = []
            for key in item['metadata']:
                if not item['metadata'][key]:
                    delete_keys.append(key)
            for key in delete_keys:
                del item['metadata'][key]

    def check_variants(self, item):
        if type(item['variants']) != int:
            item['variants'] = 0
