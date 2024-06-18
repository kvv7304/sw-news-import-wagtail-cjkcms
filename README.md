
# SW News Import Wagtail CJKCms

## Описание проекта

Проект предназначен для автоматического импорта новостей с официального сайта компании «Сибирское здоровье» (Siberian Wellness) в систему управления контентом Wagtail. Основная цель проекта заключается в упрощении и автоматизации процесса добавления новых статей и новостей на сайт, что позволяет снизить необходимость в ручной работе для администраторов.

В проекте используются несколько ключевых модулей, которые обеспечивают его функциональность. Основные модули включают:

- **Django**: Основной фреймворк, используемый для разработки веб-приложения. В частности, используется Django ORM для работы с базой данных и Django Management Commands для выполнения задач по импорту новостей.
- **Wagtail**: Система управления контентом (CMS), построенная на Django, используемая для управления страницами и контентом сайта.
- **CJKCms**: Дополнительные модули и модели, специфичные для проекта, расширяющие возможности Wagtail.

Проект функционирует на сайте https://wellness.com.ru/

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
