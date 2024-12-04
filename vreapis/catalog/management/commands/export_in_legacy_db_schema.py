from django.core.management import CommandParser
from django.core.management.base import BaseCommand, CommandError
from catalog.models import Cell
from catalog.serializers import CellSerializer


class Command(BaseCommand):
    help = 'Export designated tables in legacy db schema'


    def add_arguments(self, parser: CommandParser):
        parser.add_argument('tables', type=str, nargs='+', help='Tables to export')

    def handle(self, *args, **options):
        for table in options['tables']:
            match table:
                case 'Cell':
                    queryset = Cell.objects.all()
                    for cell in queryset:
                        serializer = CellSerializer(cell)
                        print(serializer.data)
                case _:
                    raise CommandError(f"Table {table} is not supported")
