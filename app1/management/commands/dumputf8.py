from django.core.management.base import BaseCommand
from django.core import serializers
from django.apps import apps

class Command(BaseCommand):
    help = 'Dump database data to JSON with UTF-8 encoding'

    def handle(self, *args, **options):
        excluded_models = ['auth.Permission', 'contenttypes.ContentType']

        all_models = apps.get_models()
        objects = []

        for model in all_models:
            label = f"{model._meta.app_label}.{model.__name__}"
            if label not in excluded_models:
                objects.extend(model.objects.all())

        output_file = 'datadump_utf8.json'
        with open(output_file, 'w', encoding='utf-8') as out:
            serializers.serialize('json', objects, stream=out, indent=2)

        self.stdout.write(self.style.SUCCESS(f'Data exported to {output_file} successfully.'))
