LOCATION_COOKIE = {
    'locality': '%7B%22city%22%3A%22%D0%95%D0%BA%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%BD%D0%B1%D1%83%D1%80%D0%B3%22%2C%22cityId%22%3A55%2C%22longitude%22%3A60.597474%2C%22latitude%22%3A56.838011%2C%22prefix%22%3A%22%D0%B3%22%7D'
}

START_URLS = [
    # 'https://fix-price.com/catalog/bytovaya-khimiya',
    # 'https://fix-price.com/catalog/sad-i-ogorod',
    # 'https://fix-price.com/catalog/krasota-i-zdorove',
    # 'https://fix-price.com/catalog/produkty-i-napitki/khlebobulochnye-izdeliya',
    'https://fix-price.com/catalog/dlya-doma'
]

CATEGORY_API_URL = 'https://api.fix-price.com/buyer/v1/product/in/{slug}?page={page}&limit=24&sort=sold'

CATEGORY_BODY = {
    'category': 'sad-i-ogorod/gorshki-i-kashpo',
    'brand': [],
    'price': [],
    'isDividedPrice': False,
    'isNew': False,
    'isHit': False,
    'isSpecialPrice': False,
}

CATEGORY_HEADERS = {
    'authority': 'api.fix-price.com',
    'accept': 'application/json, text/plain, */*',
    'content-type': 'application/json',
    'origin': 'https://fix-price.com',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/108.0.0.0 (Edition Yx 05)',
    'x-city': '55',
    'x-key': 'be7198c8e2459ceeb8ab9db0c92f3e30',
    'x-language': 'ru',
}

PRODUCT_FORMAT_URL = "https://fix-price.com/catalog/{product_slug}"
PRODUCT_DESCRIPTION = "//div[@itemscope='itemscope']//div[@class = 'description']/text()"
PRODUCT_SECTIONS = "//div[contains(@class, 'breadcrumbs')]/div[contains(@class, 'crumb')]//span[@itemprop='name']/text()"

PRODUCT_CHARACTERISTICS = "//div[@class='additional-information']//p[@class='property']"
PRODUCT_CHARACTERISTIC_TITLE = "//span[@class='title']/text()"
PRODUCT_CHARACTERISTIC_VALUE = "//span[@class='value']/text()"

SCRIPT_NUXT = "//script[contains(text(), 'window.__NUXT__')]"
PRODUCT_MARKETING_TAGS = "//div[@class='product-images']//div[@class='wrapper sticker']//div[@data-test='sticker']/text()"

PRODUCT_CARD_PRICE = "//div[@class='price-quantity-block']//div[@class='sticker' and text()='По карте «Fix Price»']/preceding-sibling::div[@class='price-in-cart']/div[@class='special-price']/text()"
