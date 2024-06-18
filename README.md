
# SW News Import Wagtail CJKCms

## Описание проекта

Проект предназначен для автоматического импорта новостей с официального сайта компании «Сибирское здоровье» (Siberian Wellness) в систему управления контентом Wagtail. Основная цель проекта заключается в упрощении и автоматизации процесса добавления новых статей и новостей на сайт, что позволяет снизить необходимость в ручной работе для администраторов.

Система состоит из нескольких компонентов, которые взаимодействуют между собой для достижения поставленных целей:

- **Получение данных из Backoffice**: Сбор данных о новостях с помощью веб-скрейпинга и API запросов.
- **Обработка и парсинг данных**: Очистка и структурирование полученной информации для дальнейшей обработки.
- **Импорт в Wagtail**: Создание и публикация новых статей на сайте Wagtail с использованием модели данных Wagtail.

Проект функционирует на сайте https://wellness.com.ru/

## Установка и настройка

1. Клонируйте репозиторий:
   ```sh
   git clone https://github.com/kvv7304/sw-news-import-wagtail-cjkcms.git
   cd sw-news-import-wagtail-cjkcms
   ```

2. Установите зависимости:
   ```sh
   pip install -r requirements.txt
   ```

3. Настройте конфигурационные файлы, в файле `config.py` укажите ваши данные для авторизации и ключи капчи.
   ```sh
   Пример ключа капчи
   CAPTCHA_KEY = "sample_captcha_key"
   Пример данных пользователя
   USER = {
          "number": "sample_number",
          "password": "sample_password"
   }
   ```

## Использование

### Основные команды

#### add_main

Команда `add_main` предназначена для автоматического добавления новых статей на сайт Wagtail. Она выполняет следующие действия:

1. **Получение данных новостей**: Команда обращается к backoffice сайту Siberian Wellness и получает список новостей.
2. **Создание статьи**: Для каждой новости создается новая статья в Wagtail с использованием модели `ProjectArticlePage`.
3. **Загрузка изображений**: Если новость содержит изображение, оно скачивается и добавляется к статье.
4. **Публикация статьи**: Новая статья сохраняется и публикуется на сайте.

### Использование команды add_main

Администратор сайта может использовать команду `add_main` для автоматического добавления новостей на сайт. Пример использования команды:

```sh
python manage.py add_main
```

Команда `add_main` выполняет следующие шаги:

1. **Получение данных из Backoffice**: Команда использует учетные данные, указанные в конфигурационном файле, чтобы получить доступ к Backoffice и собрать данные о новостях.
2. **Создание и публикация статьи**: На основе полученных данных создаются новые статьи, которые затем публикуются на сайте.
