import pprint
from io import BytesIO
import requests
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.utils import timezone
from wagtail.images.models import Image
from wagtail.models import Page
from wagtail.blocks import StreamValue, RichTextBlock, StructBlock, PageChooserBlock
from cjkcms.models import ReusableContent  # Добавлен импорт модели ReusableContent
from home.models import ProjectArticlePage
from swblog.management.commands.backoffice import backoffice_page_news_list, backoffice_page_news

def download_and_save_image(image_url, title):
    response = requests.get(image_url)
    if response.status_code == 200:
        image_stream = BytesIO(response.content)
        wagtail_image = Image.objects.create(
            title=title,
            file=ImageFile(image_stream, name=title)
        )
        wagtail_image.save()
        return wagtail_image
    else:
        raise Exception("Image download failed with status code {}".format(response.status_code))

class Command(BaseCommand):
    help = 'Добавляет новую статью с изображением на сайт Wagtail'

    def handle(self, *args, **kwargs):
        if 'title' not in kwargs:
            return

        description = f"Узнайте все о {kwargs['title']} с компанией Сибирское здоровье (Siberian Wellness). " \
                      f"Ключевые темы: {kwargs['caption']}. "\
                      f"Присоединяйтесь к нашему сообществу и откройте для себя все возможности продукции и бизнеса. " \
                      f"Читайте последние новости и обновления о {kwargs['title']}. " \
                      f"Узнайте больше на сайте Знайкиной Марины и начните ваш путь к успеху с Сибирское здоровье (Siberian Wellness)."

        owner = User.objects.get(username=kwargs['owner_username'])
        parent_page = Page.objects.get(id=kwargs['parent_page_id'])
        new_article = self.create_and_publish_article(
            title=kwargs['title'],
            seo_title=kwargs['title'],
            search_description=description,
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
                    f'<div class="block-text">'
                    f'<p data-block-key="8hxso">'
                    f'{backoffice_page_news(kwargs["url"])}'
                    f'</p>'
                    f'</div>'
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

        response_data = {
            "body": new_article.body,
        }
        print(response_data)


        if kwargs['image_url'] and new_article:
            image_url = kwargs['image_url']
            image_title = kwargs['slug'] + "." + image_url.split(".")[-1]
            wagtail_image = download_and_save_image(image_url, image_title)
            new_article.cover_image = wagtail_image
            new_article.og_image = wagtail_image

        new_article.save_revision().publish()

    def create_and_publish_article(self, title, slug, body, caption, owner, seo_title, search_description,
                                   canonical_url, date_display, parent_page, custom_template):
        if not parent_page.get_children().exists():
            first_article = ProjectArticlePage(
                title="Temporary Article",
                slug="temporary-article",
                seo_title="temporary-article",
                search_description="Temporary Article",
                canonical_url="https://wellness.com.ru/temporary-article",
                body="",
                caption="",
                owner=owner,
                date_display=timezone.now(),
                custom_template="cjkcms/pages/web_page.html",
            )
            first_article.depth = parent_page.depth + 1
            first_article.path = parent_page.path + '0001'
            first_article.save()

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

        parent_page.add_child(instance=new_article)
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
            image_url=data['image_url'],
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
