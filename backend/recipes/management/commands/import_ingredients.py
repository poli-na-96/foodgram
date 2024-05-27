import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортировать ингредиенты из CSV файла'

    def handle(self, *args, **options):
        csv_file = os.path.join(settings.BASE_DIR, 'data', 'ingredients.csv')

        with open(csv_file, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                name, measurement_unit = row
                ingredient, created = Ingredient.objects.get_or_create(
                    name=name.strip(),
                    measurement_unit=measurement_unit.strip()
                )
                if not created:
                    ingredient.measurement_unit = measurement_unit.strip()
                    ingredient.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Импортированные ингредиенты: {name,measurement_unit}'
                    )
                )
