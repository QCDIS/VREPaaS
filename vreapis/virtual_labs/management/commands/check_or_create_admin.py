from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
import os


class Command(BaseCommand):
    help = "Creates an admin user non-interactively if it doesn't exist"

    def add_arguments(self, parser):
        parser.add_argument('--username', help="Admin's username")
        parser.add_argument('--email', help="Admin's email")

    def handle(self, *args, **options):
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", default="change_me_please")
        self.stdout.write(f"Admin password from ENV {password}")
        User = get_user_model()
        if not User.objects.filter(username=options['username']).exists():
            self.stdout.write(f"Admin user {options['username']} not present, creating it ...")
            user = User.objects.create_superuser(username=options['username'], email=options['email'])
            user.set_password(password)
            user.save()
            self.stdout.write(f"Admin user {options['username']} created!")
