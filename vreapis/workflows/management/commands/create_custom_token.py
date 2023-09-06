import os

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Create a custom token for a specific user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username of the user')
        parser.add_argument('--token_env_var', type=str, help='Name of the environment variable containing the token')

    def handle(self, *args, **options):

        self.stdout.write(self.style.ERROR('------------------------------Create Custom Token------------------------------'))
        username = options['username']
        password = os.environ.get("DJANGO_USER_PASSWORD", default="change_me_please")
        token_env_var = options['token_env_var']
        self.stdout.write(
            self.style.ERROR('token_env_var: '+token_env_var))
        token_key = os.environ.get(token_env_var)

        User = get_user_model()
        if not User.objects.filter(username=options['username']).exists():
            self.stdout.write(f"User {options['username']} not present, creating it ...")
            user = User.objects.create_superuser(username=options['username'])
            user.set_password(password)
            user.save()
            self.stdout.write(f"user {options['username']} created!")

        if token_key:
            token, created = Token.objects.get_or_create(user=user, key=token_key)
            self.stdout.write(self.style.SUCCESS(f'Token created for user: {username}'))
            self.stdout.write(self.style.SUCCESS(f'Token key: {token.key}'))
        else:
            self.stdout.write(self.style.ERROR('Token environment variable not found.'))



