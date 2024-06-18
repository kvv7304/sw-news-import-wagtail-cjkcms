from django.core.management.base import BaseCommand, CommandError
from home.models import ProjectArticlePage

class Command(BaseCommand):
    help = 'Exports all published articles from the site'

    def add_arguments(self, parser):
        parser.add_argument('id', type=int, help='ID of the article to be exported')

    def handle(self, *args, **options):
        article_id = options['id']
        try:
            article = ProjectArticlePage.objects.get(id=article_id)
        except ProjectArticleIndex.DoesNotExist:
            raise CommandError(f'Article with id {article_id} does not exist')

        for field in article._meta.fields:
            field_name = field.name
            field_value = getattr(article, field_name, None)
            if field_value:
                self.stdout.write(f"{field_name}: {field_value}")
        response_data = {"body": article.body}
        print(response_data)
