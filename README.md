## Установка проекта
Установка производится копированием ссылки репозитория и установкой зависимостей командой 
`pip install -r requirements.txt`
## Запуск парсера 
Производится путем перехода в рабочий каталог проекта и вводом команды в терминал
`scrapy crawl fix-price -O results.json`
Или созданием конфигурации запуска со следующими настройками 
- module -> scrapy
- parametres -> crawl fix-price -O results.json
- Working directory -> ../my_parsers
