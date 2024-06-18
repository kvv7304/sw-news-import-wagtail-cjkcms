
FROM python:3.11-slim
WORKDIR /django_app/

# Установка зависимостей
COPY . .
RUN python3 -m pip install --no-cache-dir --no-warn-script-location --upgrade pip \
    && python3 -m pip install --no-cache-dir --no-warn-script-location --user -r requirements.txt

# Установка cron и создание cron задания
RUN apt-get update && apt-get install -y cron \
    && echo "0 * * * * cd /django_app && /usr/local/bin/python3 manage.py add_main >> /var/log/cron.log 2>&1" >> /etc/cron.d/django-cron \
    && chmod 0644 /etc/cron.d/django-cron \
    && crontab /etc/cron.d/django-cron

# Запуск cron и приложения
CMD cron && python3 manage.py runserver 0.0.0.0:8081
