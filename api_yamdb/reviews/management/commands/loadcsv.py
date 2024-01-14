from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.shortcuts import get_object_or_404
from django.apps import apps
from django.conf import settings
import csv


FOREIGNKEY_FIELDS = ("category", "author", "genre", "title", "review")
DATA_DIR = settings.BASE_DIR / "static" / "data"
FILE_NAMES = [
    "category.csv",
    "genre.csv",
    "titles.csv",
    "genre_title.csv",
    "users.csv",
    "review.csv",
    "comments.csv",
]


class Command(BaseCommand):
    help = """Импортировать данные из файла model.csv в модель model.
        Пример: python3 manage.py loadcsv title.csv.
        Файлы моделей берутся из BASE_DIR / static / data"""

    def get_csv_file(self, filename):
        file_path = settings.BASE_DIR / "static" / "data" / filename
        return file_path

    def get_model_name(self, file_name):
        model_name = file_name.rstrip(".csv")
        if "_" in model_name:
            model_name = model_name.replace("_", "")
        return model_name

    def get_model(self, model_name):
        if model_name == "author":
            Model = apps.get_model("reviews", "user")
        else:
            Model = apps.get_model("reviews", model_name)
        if not Model:
            raise CommandError(f"Модели {Model} не существует")
        return Model

    def load_csv(self, file_name):
        model_name = self.get_model_name(file_name)
        file_path = self.get_csv_file(file_name)
        Model = self.get_model(model_name)
        try:
            with open(file_path) as file:
                self.stdout.write(f"Чтение файла {file_name}")
                reader = csv.DictReader(file)
                for row in reader:
                    Obj = Model()
                    for i, field in enumerate(row.values()):
                        if reader.fieldnames[i] in FOREIGNKEY_FIELDS:
                            model = self.get_model(reader.fieldnames[i])
                            obj = get_object_or_404(model, id=field)
                            setattr(Obj, reader.fieldnames[i], obj)
                        else:
                            setattr(Obj, reader.fieldnames[i], field)
                    Obj.save()
        except Exception as e:
            raise CommandError(
                f"При чтении файла {file_name} произошла ошибка: {e}"
            )

    def handle(self, *args, **options):
        for file_name in FILE_NAMES:
            self.load_csv(file_name)
