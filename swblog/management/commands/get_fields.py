from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from home.models import ProjectArticlePage
from wagtail.core.models import Page


class Command(BaseCommand):
    help = 'Exports all published articles from the site'

    def handle(self, *args, **options):
        try:
            # Попробуйте получить экземпляр ProjectArticlePage с id=17
            article = ProjectArticlePage.objects.get(id=17)

            # Выводим поля страницы
            for field in article._meta.fields:
                field_name = field.name
                field_value = getattr(article, field_name, None)
                print(f"{field_name}: {field_value}")

            # Получаем дочерние страницы
            children = article.get_children().live()  # Используем live() для получения только опубликованных страниц

            print("\nДочерние страницы:")
            for child in children:
                print(f"ID: {child.id}, Заголовок: {child.title}, Тип: {child.specific_class.__name__}")
        except ProjectArticlePage.DoesNotExist:
            self.stdout.write(self.style.ERROR('ProjectArticlePage с указанным id не существует'))

            # Печать всех существующих ProjectArticlePage для отладки
            existing_articles = ProjectArticlePage.objects.all()
            print("\nСуществующие ProjectArticlePage:")
            for article in existing_articles:
                print(f"ID: {article.id}, Заголовок: {article.title}")


def create_and_publish_article(self, title, parent_page):
    # Создание новой статьи
    new_article = ProjectArticlePage(
        title=title,
        slug=slugify(title),
        # добавьте другие обязательные поля здесь
    )
    parent_page.add_child(instance=new_article)
    new_article.save_revision().publish()


class AddMainJobCommand(BaseCommand):
    help = 'Adds main job'

    def handle(self, *args, **kwargs):
        try:
            parent_page = Page.objects.get(slug='parent-page-slug')
        except Page.DoesNotExist:
            raise CommandError('Parent page does not exist')

        if not parent_page:
            self.stdout.write(self.style.ERROR('Parent page not found'))
            return

        # Добавьте статью
        self.create_and_publish_article(title="New Article Title", parent_page=parent_page)


def start():
    from django.core.management import call_command
    call_command('add_main_job')
