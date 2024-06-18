from io import BytesIO
import requests
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.images.models import Image
from wagtail.models import Page
from wagtail.blocks import StreamValue
from home.models import ProjectArticlePage
from swblog.management.commands.backoffice import backoffice_page_news_list, backoffice_page_news


def download_and_save_image(image_url, title):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        image_stream = BytesIO(response.content)
        wagtail_image = Image.objects.create(
            title=title,
            file=ImageFile(image_stream, name=title)
        )
        wagtail_image.save()
        return wagtail_image
    except requests.RequestException as e:
        raise Exception(f"Image download failed: {str(e)}")


class Command(BaseCommand):
    help = 'Добавляет новую статью с изображением на сайт Wagtail'

    def handle(self, *args, **kwargs):
        required_params = ['title', 'caption', 'slug', 'url', 'date_display', 'owner_username', 'parent_page_id',
                           'custom_template', 'description']
        missing_params = [param for param in required_params if param not in kwargs]

        if missing_params:
            self.stderr.write(f"Missing required parameters: {', '.join(missing_params)}")
            return

        try:
            owner = User.objects.get(username=kwargs['owner_username'])
            parent_page = Page.objects.get(id=kwargs['parent_page_id'])
        except User.DoesNotExist:
            self.stderr.write(f"User {kwargs['owner_username']} does not exist")
            return
        except Page.DoesNotExist:
            self.stderr.write(f"Page with ID {kwargs['parent_page_id']} does not exist")
            return

        new_article = self.create_and_publish_article(
            title=kwargs['title'],
            seo_title=kwargs['title'],
            search_description=kwargs['description'],
            slug=kwargs['slug'],
            canonical_url=f"https://wellness.com.ru/{kwargs['slug']}",
            body=None,
            caption=kwargs['caption'],
            date_display=kwargs['date_display'],
            owner=owner,
            parent_page=parent_page,
            custom_template=kwargs['custom_template'],
        )

        body = [
            {
                "type": "text",
                "value": (
                    f'{backoffice_page_news(kwargs["url"])}'
                )
            },
            {
                "type": "reusable_content",
                "value": {
                    "settings": {"custom_id": "1"},
                    "content": 1
                }
            }
        ]

        new_article.body = StreamValue(new_article.body.stream_block, body, is_lazy=True)
        new_article.save_revision().publish()

        if kwargs.get('image_url'):
            image_url = kwargs['image_url']
            image_title = f"{kwargs['slug']}.{image_url.split('.')[-1]}"
            wagtail_image = download_and_save_image(image_url, image_title)
            new_article.cover_image = wagtail_image
            new_article.og_image = wagtail_image

        new_article.save_revision().publish()

    def create_and_publish_article(self, title, slug, body, caption, owner, seo_title, search_description,
                                   canonical_url, date_display, parent_page, custom_template):

        new_article = ProjectArticlePage(
            title=title,
            seo_title=seo_title,
            search_description=search_description,
            slug=slug,
            canonical_url=canonical_url,
            body=body,
            caption=caption,
            owner=owner,
            date_display=date_display,
            custom_template=custom_template,
        )

        if not parent_page.get_children().exists():
            # Если у родительской страницы нет дочерних элементов, создаем путь и глубину вручную
            new_article.depth = parent_page.depth + 1
            new_article.path = parent_page.path + '0001'
            new_article.save()
            parent_page.refresh_from_db()  # Обновляем parent_page чтобы избежать ошибок сохранения
        else:
            parent_page.add_child(instance=new_article)

        # Публикуем статью после добавления в базу данных
        new_article.save_revision().publish()

        return new_article


command_instance = Command()
data_backoffice = backoffice_page_news_list()
for data in reversed(data_backoffice):
    try:
        command_instance.handle(
            title=data['title'],
            slug=data['slug'],
            url=data["body_url"],
            caption=data['caption_tag'],
            description=data['description'],
            image_url=data.get('image_url', ''),
            date_display=data['date_display'],
            owner_username="kv7304",
            parent_page_id=17,
            custom_template="cjkcms/pages/web_page.html"
        )
    except ValidationError as e:
        if 'slug' not in e.error_dict:
            print(
                f"Ошибка в {data['title']}: "
                f"{' '.join(message for messages in e.message_dict.values() for message in messages)}")
        continue
