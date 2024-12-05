import json
import os.path

from django.core.management import CommandParser
from django.core.management.base import BaseCommand, CommandError
from django.db.models import QuerySet

from catalog.models import Cell
from catalog.serializers import CellSerializer


class Command(BaseCommand):
    help: str = 'Export designated tables in legacy db schema'


    def add_arguments(self, parser: CommandParser):
        parser.add_argument('tables', type=str, nargs='+', help='Tables to export')

    def handle(self, *args, **options):
        for table in options['tables']:
            match table:
                case 'Cell':
                    queryset: QuerySet = Cell.objects.all()
                    no: int = 1
                    cells: dict[str, dict] = {}
                    for cell in queryset:
                        serializer = CellSerializer(cell)
                        cells[str(no)] = serializer.data
                    db_file: str = os.path.expanduser('~/NaaVRE/NaaVRE_db.json')
                    with open(db_file) as f:
                        db = json.load(f)
                        db['cells'] = cells
                    with open(db_file, 'w') as f:
                        json.dump(db, f)
                case _:
                    raise CommandError(f"Table {table} is not supported")