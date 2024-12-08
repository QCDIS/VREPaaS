import json

from django.core.management import CommandParser
from django.core.management.base import BaseCommand, CommandError
from django.db.models import QuerySet

import common
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
                    print(f'Cell count: {queryset.count()}')
                    no: int = 1
                    cells: dict[str, dict] = {}
                    for cell in queryset:
                        serializer = CellSerializer(cell)
                        print(f'task_name: {cell.task_name}')
                        cells[str(no)] = serializer.data
                        no += 1
                    db_file: str = f'{common.project_root}/NaaVRE_db.json'
                    with open(db_file) as f:
                        db = json.load(f)
                        db['cells'] = cells
                    with open(db_file, 'w') as f:
                        json.dump(db, f)
                case _:
                    raise CommandError(f"Table {table} is not supported")
